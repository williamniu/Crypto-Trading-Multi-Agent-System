from __future__ import annotations

from typing import Any

from app.config.settings import Settings, load_settings
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.services.llm_client import LLMClient
from app.agents.risk_officer.tools.approve_plan_tool import ApprovePlanTool
from app.agents.risk_officer.tools.calc_position_size_tool import CalcPositionSizeTool
from app.agents.risk_officer.tools.check_exposure_tool import CheckExposureTool
from app.services.risk_service import RiskService


class RiskOfficerToolset:
    """MVP risk checks for sizing, exposure and approval."""

    def __init__(
        self,
        risk_service: RiskService | None = None,
        *,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.risk_service = risk_service or RiskService(settings=self.settings)
        self.llm_client = llm_client or LLMClient(settings=self.settings)
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

        report = {
            "position_size": sizing["position_size"],
            "risk_amount": sizing["risk_amount"],
            "total_exposure": exposure["total_exposure"],
            "exposure_ok": exposure["exposure_ok"],
            "approved": approval["approved"],
            "reasons": approval["reasons"],
        }
        return self._maybe_add_llm_summary(
            report=report,
            risk_settings=risk_settings,
            draft_plan=draft_plan,
            trace=trace,
        )

    def _maybe_add_llm_summary(
        self,
        *,
        report: dict[str, Any],
        risk_settings: dict[str, float],
        draft_plan: dict[str, Any],
        trace: ExecutionTrace | None,
    ) -> dict[str, Any]:
        if not (self.llm_client.enabled and self.settings.llm_enable_risk):
            return report

        payload = {
            "risk_profile": risk_settings,
            "draft_plan": {
                "action": draft_plan.get("action"),
                "stop_loss_pct": draft_plan.get("stop_loss_pct"),
                "take_profit_pct": draft_plan.get("take_profit_pct"),
                "rr_ratio": draft_plan.get("rr_ratio"),
                "target_exposure": draft_plan.get("target_exposure"),
            },
            "risk_report": report,
        }
        llm_result = self.llm_client.generate(
            "Review the risk snapshot and explain the approval outcome.",
            constraints={
                "do_not_change_approval": report["approved"],
                "do_not_change_reasons": report["reasons"],
                "max_sentences": 2,
            },
            system_prompt=(
                "You are the risk officer in a constrained trading system. "
                "Use only the provided risk profile, draft plan, and deterministic risk report. "
                "Do not override approval, sizing, exposure, or reasons. "
                "Return a concise explanation of the current risk posture."
            ),
        )
        llm_summary = str(llm_result.get("message", "")).strip()
        if trace is not None:
            trace.add_tool_call(
                agent="risk_officer",
                tool_name="llm_risk_analysis",
                payload=payload,
                output={"llm_summary": llm_summary},
            )
        if not llm_summary:
            return report
        return {**report, "llm_summary": llm_summary}
