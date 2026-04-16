from __future__ import annotations

import json

from app.config.settings import load_settings
from app.workflows.master_workflow import MasterWorkflow


def build_sample_task() -> dict[str, object]:
    settings = load_settings()
    return {
        "task_id": "demo-task-001",
        "symbol": settings.default_symbol,
        "timeframe": settings.default_timeframe,
        "objective": "analyze_trade_setup",
        "risk": {
            "account_balance": settings.default_account_balance,
            "risk_per_trade": settings.default_risk_per_trade,
            "current_exposure": settings.default_current_exposure,
            "max_exposure": settings.default_max_exposure,
        },
    }


def main() -> None:
    workflow = MasterWorkflow(settings=load_settings())
    result = workflow.run(build_sample_task())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
