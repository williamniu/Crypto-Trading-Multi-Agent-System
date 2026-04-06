from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import FunctionTool
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry


class RiskOfficerToolset:
	"""MVP risk checks for sizing, exposure and approval."""

	def __init__(self) -> None:
		self.registry = ToolRegistry()
		self.registry.register_many(
			[
				FunctionTool(
					name="calc_position_size",
					description="Calculate risk-based position size.",
					required_fields=["account_balance", "risk_per_trade", "stop_loss_pct"],
					handler=self._calc_position_size,
				),
				FunctionTool(
					name="check_exposure",
					description="Ensure total exposure is below max threshold.",
					required_fields=["current_exposure", "new_exposure", "max_exposure"],
					handler=self._check_exposure,
				),
				FunctionTool(
					name="approve_plan",
					description="Return final approve/reject decision.",
					required_fields=["exposure_ok", "rr_ratio"],
					handler=self._approve_plan,
				),
			]
		)

	@staticmethod
	def _calc_position_size(payload: dict[str, Any]) -> dict[str, Any]:
		balance = float(payload["account_balance"])
		risk_per_trade = float(payload["risk_per_trade"])
		stop_loss_pct = max(float(payload["stop_loss_pct"]), 0.0001)
		risk_amount = balance * risk_per_trade
		position_size = risk_amount / stop_loss_pct
		return {
			"risk_amount": round(risk_amount, 2),
			"position_size": round(position_size, 2),
		}

	@staticmethod
	def _check_exposure(payload: dict[str, Any]) -> dict[str, Any]:
		total = float(payload["current_exposure"]) + float(payload["new_exposure"])
		max_exposure = float(payload["max_exposure"])
		return {"total_exposure": round(total, 4), "exposure_ok": total <= max_exposure}

	@staticmethod
	def _approve_plan(payload: dict[str, Any]) -> dict[str, Any]:
		exposure_ok = bool(payload["exposure_ok"])
		rr_ratio = float(payload["rr_ratio"])
		approved = exposure_ok and rr_ratio >= 1.5
		reasons = []
		if not exposure_ok:
			reasons.append("Exposure exceeds max threshold")
		if rr_ratio < 1.5:
			reasons.append("Risk/reward ratio below 1.5")
		if not reasons:
			reasons.append("Plan meets MVP risk rules")
		return {"approved": approved, "reasons": reasons}

	def review_plan(
		self,
		task: dict[str, Any],
		draft_plan: dict[str, Any],
		trace: ExecutionTrace | None = None,
	) -> dict[str, Any]:
		risk_settings = task.get("risk", {})
		account_balance = float(risk_settings.get("account_balance", 10000))
		risk_per_trade = float(risk_settings.get("risk_per_trade", 0.01))
		stop_loss_pct = float(draft_plan.get("stop_loss_pct", 0.01))

		sizing = self.registry.execute(
			tool_name="calc_position_size",
			payload={
				"account_balance": account_balance,
				"risk_per_trade": risk_per_trade,
				"stop_loss_pct": stop_loss_pct,
			},
			trace=trace,
			agent_name="risk_officer",
		)

		exposure = self.registry.execute(
			tool_name="check_exposure",
			payload={
				"current_exposure": float(risk_settings.get("current_exposure", 0.1)),
				"new_exposure": float(draft_plan.get("target_exposure", 0.05)),
				"max_exposure": float(risk_settings.get("max_exposure", 0.3)),
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
