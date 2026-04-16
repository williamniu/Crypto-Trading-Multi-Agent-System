from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StubLLMClient:
    """Reserved interface for later constrained-LLM expansion."""

    enabled: bool = False

    def generate(
        self,
        prompt: str,
        *,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "mode": "stub",
            "enabled": self.enabled,
            "message": "LLM integration is intentionally disabled in the deterministic MVP.",
            "prompt_preview": prompt[:120],
            "constraints": constraints or {},
        }
