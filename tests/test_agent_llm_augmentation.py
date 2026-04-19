from app.agents.master.agent import MasterAgent
from app.agents.risk_officer.toolset import RiskOfficerToolset
from app.agents.sentiment_analyst.toolset import SentimentAnalystToolset
from app.agents.ta_analyst.toolset import TAAnalystToolset
from app.config.settings import Settings


class StubLLMClient:
    enabled = True

    def __init__(self, *, message: str, settings: Settings) -> None:
        self.message = message
        self.settings = settings

    def generate(self, prompt: str, *, constraints=None, system_prompt=None):  # noqa: ANN001
        return {
            "enabled": True,
            "mode": "openai_compatible",
            "message": self.message,
            "constraints": constraints or {},
            "system_prompt": system_prompt or "",
            "prompt_preview": prompt[:80],
        }


def test_ta_toolset_adds_llm_summary_when_enabled() -> None:
    settings = Settings(llm_mode="openai_compatible", llm_api_key="x", llm_base_url="https://llm.example.com", llm_model="gpt-test")
    toolset = TAAnalystToolset(
        settings=settings,
        llm_client=StubLLMClient(message="TA looks constructive above support.", settings=settings),
    )

    report = toolset.generate_report({"symbol": "BTCUSDT", "timeframe": "1h"})

    assert report["llm_summary"] == "TA looks constructive above support."


def test_sentiment_toolset_adds_llm_summary_when_enabled() -> None:
    settings = Settings(llm_mode="openai_compatible", llm_api_key="x", llm_base_url="https://llm.example.com", llm_model="gpt-test")
    toolset = SentimentAnalystToolset(
        settings=settings,
        llm_client=StubLLMClient(message="Sentiment remains net positive across headlines.", settings=settings),
    )

    report = toolset.generate_report({"symbol": "BTCUSDT"})

    assert report["llm_summary"] == "Sentiment remains net positive across headlines."


def test_risk_toolset_adds_llm_summary_when_enabled() -> None:
    settings = Settings(llm_mode="openai_compatible", llm_api_key="x", llm_base_url="https://llm.example.com", llm_model="gpt-test")
    toolset = RiskOfficerToolset(
        settings=settings,
        llm_client=StubLLMClient(message="Risk posture is acceptable within current exposure limits.", settings=settings),
    )

    report = toolset.review_plan(
        task={
            "risk": {
                "account_balance": 10_000,
                "risk_per_trade": 0.01,
                "current_exposure": 0.10,
                "max_exposure": 0.30,
            }
        },
        draft_plan={"stop_loss_pct": 0.01, "target_exposure": 0.05, "rr_ratio": 2.0},
    )

    assert report["llm_summary"] == "Risk posture is acceptable within current exposure limits."


def test_master_agent_adds_trade_plan_llm_summary_when_enabled() -> None:
    settings = Settings(llm_mode="openai_compatible", llm_api_key="x", llm_base_url="https://llm.example.com", llm_model="gpt-test")
    agent = MasterAgent(
        llm_client=StubLLMClient(message="The final BUY plan is supported by aligned signals and acceptable risk.", settings=settings),
    )

    result = agent.run(
        {
            "task_id": "task-llm-001",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "risk": {
                "account_balance": 10_000,
                "risk_per_trade": 0.01,
                "current_exposure": 0.10,
                "max_exposure": 0.30,
            },
        }
    )

    assert (
        result["trade_plan"]["llm_summary"]
        == "The final BUY plan is supported by aligned signals and acceptable risk."
    )
