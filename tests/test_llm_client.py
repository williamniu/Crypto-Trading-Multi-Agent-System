from app.config.settings import Settings
from app.services.llm_client import LLMClient


class StubHTTPClient:
    def request_json(self, *, method: str, url: str, headers: dict[str, str], body: dict[str, object]) -> dict[str, object]:
        assert method == "POST"
        assert url == "https://llm.example.com/chat/completions"
        assert headers["Authorization"] == "Bearer test-key"
        assert body["model"] == "gpt-test"
        return {
            "choices": [
                {
                    "message": {
                        "content": "The deterministic plan remains BUY because TA and sentiment align."
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 12},
        }


def test_llm_client_stub_mode_returns_placeholder() -> None:
    client = LLMClient(settings=Settings())

    result = client.generate("hello")

    assert result["mode"] == "stub"
    assert result["enabled"] is False


def test_llm_client_openai_compatible_mode_calls_api() -> None:
    client = LLMClient(
        settings=Settings(
            llm_mode="openai_compatible",
            llm_base_url="https://llm.example.com",
            llm_api_key="test-key",
            llm_model="gpt-test",
        ),
        http_client=StubHTTPClient(),
    )

    result = client.generate("summarize", constraints={"max_sentences": 1})

    assert result["enabled"] is True
    assert result["model"] == "gpt-test"
    assert "deterministic plan" in result["message"]
