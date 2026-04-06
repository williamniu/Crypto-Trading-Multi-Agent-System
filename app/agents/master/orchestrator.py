from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.risk_officer.toolset import RiskOfficerToolset
from app.agents.sentiment_analyst.toolset import SentimentAnalystToolset
from app.agents.ta_analyst.toolset import TAAnalystToolset


class MasterOrchestrator:
	"""Coordinates TA, sentiment and risk modules into a final trade plan."""

	def __init__(
		self,
		ta_toolset: TAAnalystToolset | None = None,
		sentiment_toolset: SentimentAnalystToolset | None = None,
		risk_toolset: RiskOfficerToolset | None = None,
	) -> None:
		self.ta_toolset = ta_toolset or TAAnalystToolset()
		self.sentiment_toolset = sentiment_toolset or SentimentAnalystToolset()
		self.risk_toolset = risk_toolset or RiskOfficerToolset()

	def run(self, task: dict[str, Any]) -> dict[str, Any]:
		trace = ExecutionTrace(run_id=str(uuid4()))
		trace.add_stage("start")

		ta_report = self.ta_toolset.generate_report(task, trace=trace)
		trace.add_stage("ta_complete")

		sentiment_report = self.sentiment_toolset.generate_report(task, trace=trace)
		trace.add_stage("sentiment_complete")

		draft_plan = self._synthesize_trade_plan(task, ta_report, sentiment_report)
		trace.add_stage("draft_plan_complete")

		risk_report = self.risk_toolset.review_plan(task, draft_plan, trace=trace)
		trace.add_stage("risk_complete")

		final_plan = {
			**draft_plan,
			"position_size": risk_report["position_size"],
			"approved": risk_report["approved"],
			"reasons": risk_report["reasons"],
			"risk_amount": risk_report["risk_amount"],
		}

		if not final_plan["approved"]:
			final_plan["action"] = "HOLD"

		trace.add_stage("complete")
		trace.complete()

		return {
			"task": task,
			"ta_report": ta_report,
			"sentiment_report": sentiment_report,
			"risk_report": risk_report,
			"trade_plan": final_plan,
			"trace": trace.to_dict(),
		}

	@staticmethod
	def _synthesize_trade_plan(
		task: dict[str, Any],
		ta_report: dict[str, Any],
		sentiment_report: dict[str, Any],
	) -> dict[str, Any]:
		symbol = task.get("symbol", "BTCUSDT")
		signal = ta_report["signal"]
		sentiment_score = sentiment_report["sentiment_score"]

		ta_bias = 1 if signal == "bullish" else -1
		combined_score = round(0.7 * ta_bias + 0.3 * sentiment_score, 3)

		action = "BUY" if combined_score > 0.1 else "SELL"
		stop_loss_pct = 0.01 if action == "BUY" else 0.012
		take_profit_pct = 0.02 if action == "BUY" else 0.024
		rr_ratio = round(take_profit_pct / stop_loss_pct, 2)

		return {
			"symbol": symbol,
			"action": action,
			"confidence": round((ta_report["confidence"] + abs(sentiment_score)) / 2, 2),
			"combined_score": combined_score,
			"entry_hint": "market",
			"stop_loss_pct": stop_loss_pct,
			"take_profit_pct": take_profit_pct,
			"rr_ratio": rr_ratio,
			"target_exposure": 0.05,
			"notes": [
				f"TA signal: {signal}",
				f"Sentiment impact: {sentiment_report['event_impact']}",
			],
		}
