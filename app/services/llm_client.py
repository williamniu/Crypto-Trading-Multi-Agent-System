from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings, load_settings
from app.services.http_json_client import HTTPJSONClient


@dataclass(frozen=True)
class LLMClient:
    """Constrained LLM facade with stub and OpenAI-compatible modes."""

    settings: Settings | None = None
    http_client: HTTPJSONClient = HTTPJSONClient()

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", self.settings or load_settings())

    @property
    def enabled(self) -> bool:
        return self.settings.llm_mode != "stub"

    def generate(
        self,
        prompt: str,
        *,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self.settings.llm_mode == "stub":
            return {
                "mode": "stub",
                "enabled": False,
                "message": "LLM integration is intentionally disabled in the deterministic MVP.",
                "prompt_preview": prompt[:120],
                "constraints": constraints or {},
            }

        if self.settings.llm_mode != "openai_compatible":
            raise ValueError(f"Unsupported llm_mode: {self.settings.llm_mode}")

        if not self.settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required when llm_mode=openai_compatible")
        if not self.settings.llm_base_url:
            raise ValueError("LLM_BASE_URL is required when llm_mode=openai_compatible")
        if not self.settings.llm_model:
            raise ValueError("LLM_MODEL is required when llm_mode=openai_compatible")

        system_prompt = (
            "You are a constrained trading workflow assistant. "
            "Do not make or override decisions. "
            "Only summarize the already-decided plan in one short sentence."
        )
        user_prompt = prompt
        if constraints:
            user_prompt = f"{prompt}\n\nConstraints:\n{constraints}"

        response = self.http_client.request_json(
            method="POST",
            url=f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            body={
                "model": self.settings.llm_model,
                "temperature": self.settings.llm_temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )

        choices = response.get("choices", [])
        if not choices:
            raise ValueError("LLM response did not include any choices")

        message = choices[0].get("message", {})
        content = str(message.get("content", "")).strip()
        usage = response.get("usage", {})

        return {
            "mode": self.settings.llm_mode,
            "enabled": True,
            "model": self.settings.llm_model,
            "message": content,
            "constraints": constraints or {},
            "usage": usage,
        }
