from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool


class CalcPositionSizeTool(BaseTool):
    """Calculate position size from account risk and stop distance."""

    def __init__(self) -> None:
        super().__init__(
            name="calc_position_size",
            description="Calculate risk-based position size.",
            required_fields=["account_balance", "risk_per_trade", "stop_loss_pct"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        account_balance = float(payload["account_balance"])
        risk_per_trade = float(payload["risk_per_trade"])
        stop_loss_pct = max(float(payload["stop_loss_pct"]), 0.0001)
        risk_amount = account_balance * risk_per_trade
        position_size = risk_amount / stop_loss_pct
        return {
            "risk_amount": round(risk_amount, 2),
            "position_size": round(position_size, 2),
        }
