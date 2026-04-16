from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool
from app.agents.risk_officer.decision_policy import approve_trade_plan


class ApprovePlanTool(BaseTool):
    """Apply deterministic risk approval rules."""

    def __init__(self) -> None:
        super().__init__(
            name="approve_plan",
            description="Apply exposure and reward-to-risk approval rules.",
            required_fields=["exposure_ok", "rr_ratio"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        return approve_trade_plan(
            exposure_ok=bool(payload["exposure_ok"]),
            rr_ratio=float(payload["rr_ratio"]),
        )
