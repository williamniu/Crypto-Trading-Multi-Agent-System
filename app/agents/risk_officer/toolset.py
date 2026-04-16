from __future__ import annotations

from typing import Any

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.agents.risk_officer.tools.approve_plan_tool import ApprovePlanTool
from app.agents.risk_officer.tools.calc_position_size_tool import CalcPositionSizeTool
from app.agents.risk_officer.tools.check_exposure_tool import CheckExposureTool
from app.services.risk_service import RiskService


class RiskOfficerToolset:
    """MVP risk checks for sizing, exposure and approval."""

    def __init__(self, risk_service: RiskService | None = None) -> None:
        self.risk_service = risk_service or RiskService()
        self.registry = ToolRegistry()
        self.registry.register_many(
            [
                CalcPositionSizeTool(),
                CheckExposureTool(),
                ApprovePlanTool(),
            ]
        )

    def review_plan(
        self,
        task: dict[str, Any],
        draft_plan: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        risk_settings = self.risk_service.normalize_profile(task.get("risk"))
        stop_loss_pct = float(draft_plan.get("stop_loss_pct", 0.01))

        sizing = self.registry.execute(
            tool_name="calc_position_size",
            payload={
                "account_balance": risk_settings["account_balance"],
                "risk_per_trade": risk_settings["risk_per_trade"],
                "stop_loss_pct": stop_loss_pct,
            },
            trace=trace,
            agent_name="risk_officer",
        )

        exposure = self.registry.execute(
            tool_name="check_exposure",
            payload={
                "current_exposure": risk_settings["current_exposure"],
                "new_exposure": float(draft_plan.get("target_exposure", 0.05)),
                "max_exposure": risk_settings["max_exposure"],
            },
            trace=trace,
            agent_name="risk_officer",
        )

        approval = self.registry.execute(
            tool_name="approve_plan",
            payload={
                "exposure_ok": exposure["exposure_ok"],
                "rr_ratio": float(draft_plan.get("rr_ratio", 1.0)),
            },
            trace=trace,
            agent_name="risk_officer",
        )

        return {
            "position_size": sizing["position_size"],
            "risk_amount": sizing["risk_amount"],
            "total_exposure": exposure["total_exposure"],
            "exposure_ok": exposure["exposure_ok"],
            "approved": approval["approved"],
            "reasons": approval["reasons"],
        }
