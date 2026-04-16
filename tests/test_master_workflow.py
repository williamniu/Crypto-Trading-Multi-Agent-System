from app.schemas.trade_plan import TradePlan
from app.workflows.master_workflow import MasterWorkflow


def test_master_workflow_happy_path() -> None:
    workflow = MasterWorkflow()

    result = workflow.run(
        {
            "task_id": "task-001",
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

    trade_plan = TradePlan.model_validate(result["trade_plan"])

    assert trade_plan.action == "BUY"
    assert trade_plan.approved is True
    assert trade_plan.ta_signal == "bullish"
    assert result["trace"]["stages"] == [
        "start",
        "ta_started",
        "ta_complete",
        "sentiment_started",
        "sentiment_complete",
        "draft_plan_complete",
        "risk_started",
        "risk_complete",
        "complete",
    ]
    assert len(result["trace"]["tool_calls"]) == 9


def test_master_workflow_forces_hold_when_risk_rejects() -> None:
    workflow = MasterWorkflow()

    result = workflow.run(
        {
            "task_id": "task-002",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "risk": {
                "account_balance": 10_000,
                "risk_per_trade": 0.01,
                "current_exposure": 0.28,
                "max_exposure": 0.30,
            },
        }
    )

    assert result["trade_plan"]["action"] == "HOLD"
    assert result["trade_plan"]["approved"] is False
    assert "Exposure exceeds max threshold" in result["trade_plan"]["reasons"]
