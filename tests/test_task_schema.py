import pytest
from pydantic import ValidationError

from app.schemas.task import RiskInput, Task


def test_task_schema_instantiation_success() -> None:
    task = Task(
        task_id="task-001",
        symbol="BTCUSDT",
        risk=RiskInput(
            account_balance=10000,
            risk_per_trade=0.01,
            current_exposure=0.1,
            max_exposure=0.3,
        ),
    )

    assert task.task_id == "task-001"
    assert task.symbol == "BTCUSDT"
    assert task.timeframe == "1h"
    assert task.objective == "analyze_trade_setup"


def test_task_schema_allows_optional_or_partial_risk() -> None:
    task = Task(task_id="task-003", symbol="BTCUSDT")

    partial_task = Task(
        task_id="task-004",
        symbol="BTCUSDT",
        risk={"risk_per_trade": 0.02, "max_exposure": 0.25},
    )

    assert task.risk is None
    assert partial_task.risk is not None
    assert partial_task.risk.risk_per_trade == 0.02


def test_task_schema_invalid_timeframe() -> None:
    with pytest.raises(ValidationError):
        Task(
            task_id="task-002",
            symbol="BTCUSDT",
            timeframe="2h",
            risk={
                "account_balance": 10000,
                "risk_per_trade": 0.01,
                "current_exposure": 0.1,
                "max_exposure": 0.3,
            },
        )


def test_task_schema_invalid_risk_values() -> None:
    with pytest.raises(ValidationError):
        RiskInput(
            account_balance=-1,
            risk_per_trade=1.2,
        )
