from app.agents.risk_officer.agent import RiskOfficerAgent
from app.agents.risk_officer.toolset import RiskOfficerToolset
from app.schemas.risk_report import RiskReport


def test_risk_tool_registry_is_private_to_risk_agent() -> None:
    toolset = RiskOfficerToolset()

    assert toolset.registry.list_tools() == [
        "approve_plan",
        "calc_position_size",
        "check_exposure",
    ]


def test_risk_agent_approves_valid_plan() -> None:
    agent = RiskOfficerAgent()

    report = agent.run(
        {
            "task": {
                "risk": {
                    "account_balance": 10_000,
                    "risk_per_trade": 0.01,
                    "current_exposure": 0.10,
                    "max_exposure": 0.30,
                }
            },
            "draft_plan": {
                "stop_loss_pct": 0.01,
                "target_exposure": 0.05,
                "rr_ratio": 2.0,
            },
        }
    )
    validated = RiskReport.model_validate(report)

    assert validated.approved is True
    assert validated.position_size == 10000.0


def test_risk_agent_rejects_excess_exposure() -> None:
    agent = RiskOfficerAgent()

    report = agent.run(
        {
            "task": {
                "risk": {
                    "account_balance": 10_000,
                    "risk_per_trade": 0.01,
                    "current_exposure": 0.28,
                    "max_exposure": 0.30,
                }
            },
            "draft_plan": {
                "stop_loss_pct": 0.01,
                "target_exposure": 0.05,
                "rr_ratio": 2.0,
            },
        }
    )

    assert report["approved"] is False
    assert "Exposure exceeds max threshold" in report["reasons"]
