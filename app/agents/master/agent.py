from __future__ import annotations

from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.risk_officer.agent import RiskOfficerAgent
from app.agents.sentiment_analyst.agent import SentimentAnalystAgent
from app.agents.ta_analyst.agent import TAAnalystAgent
from app.services.llm_client import LLMClient


BUY_THRESHOLD = 0.15
SELL_THRESHOLD = -0.15
TARGET_EXPOSURE = 0.05


class MasterAgent(BaseAgent):
    """Orchestrates role-bound agents into one final trade plan."""

    def __init__(
        self,
        ta_agent: TAAnalystAgent | None = None,
        sentiment_agent: SentimentAnalystAgent | None = None,
        risk_agent: RiskOfficerAgent | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        super().__init__(name="master_agent")
        self.ta_agent = ta_agent or TAAnalystAgent()
        self.sentiment_agent = sentiment_agent or SentimentAnalystAgent()
        self.risk_agent = risk_agent or RiskOfficerAgent()
        self.llm_client = llm_client or LLMClient()

    def run(
        self,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        if trace is not None:
            trace.add_stage("ta_started")
        ta_report = self.ta_agent.run(payload, trace=trace)
        if trace is not None:
            trace.add_stage("ta_complete")
            trace.add_stage("sentiment_started")
        sentiment_report = self.sentiment_agent.run(payload, trace=trace)
        if trace is not None:
            trace.add_stage("sentiment_complete")

        draft_plan = self._synthesize_trade_plan(
            task=payload,
            ta_report=ta_report,
            sentiment_report=sentiment_report,
        )
        if trace is not None:
            trace.add_stage("draft_plan_complete")
            trace.add_stage("risk_started")
        risk_report = self.risk_agent.run(
            {"task": payload, "draft_plan": draft_plan},
            trace=trace,
        )
        if trace is not None:
            trace.add_stage("risk_complete")

        final_plan = self._finalize_trade_plan(draft_plan=draft_plan, risk_report=risk_report)
        final_plan = self._maybe_add_llm_note(
            final_plan=final_plan,
            ta_report=ta_report,
            sentiment_report=sentiment_report,
            risk_report=risk_report,
        )
        return {
            "task": payload,
            "ta_report": ta_report,
            "sentiment_report": sentiment_report,
            "risk_report": risk_report,
            "trade_plan": final_plan,
        }

    def _synthesize_trade_plan(
        self,
        *,
        task: dict[str, Any],
        ta_report: dict[str, Any],
        sentiment_report: dict[str, Any],
    ) -> dict[str, Any]:
        ta_signal = ta_report["signal"]
        ta_bias = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}[ta_signal]
        sentiment_score = float(sentiment_report["sentiment_score"])
        combined_score = round(0.7 * ta_bias + 0.3 * sentiment_score, 3)

        if combined_score >= BUY_THRESHOLD:
            action = "BUY"
        elif combined_score <= SELL_THRESHOLD:
            action = "SELL"
        else:
            action = "HOLD"

        stop_loss_pct = 0.010 if action != "SELL" else 0.012
        take_profit_pct = 0.020 if action != "SELL" else 0.024
        rr_ratio = round(take_profit_pct / stop_loss_pct, 2)
        sentiment_confidence = 0.50 + abs(sentiment_score) / 2
        confidence = round(
            min(0.95, (float(ta_report["confidence"]) + sentiment_confidence) / 2),
            2,
        )

        if action == "BUY":
            entry_hint = f"near support {ta_report['levels']['support']}"
        elif action == "SELL":
            entry_hint = f"near resistance {ta_report['levels']['resistance']}"
        else:
            entry_hint = "wait for stronger alignment"

        notes = [
            f"TA signal: {ta_signal}",
            f"Sentiment impact: {sentiment_report['event_impact']}",
        ]
        if action == "HOLD":
            notes.append("Directional conviction is below the execution threshold.")

        return {
            "task_id": task.get("task_id"),
            "symbol": task.get("symbol", "BTCUSDT"),
            "action": action,
            "confidence": confidence,
            "combined_score": combined_score,
            "entry_hint": entry_hint,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
            "rr_ratio": rr_ratio,
            "target_exposure": TARGET_EXPOSURE,
            "notes": notes,
            "ta_signal": ta_signal,
            "sentiment_score": sentiment_score,
        }

    @staticmethod
    def _finalize_trade_plan(
        *,
        draft_plan: dict[str, Any],
        risk_report: dict[str, Any],
    ) -> dict[str, Any]:
        approved = bool(risk_report["approved"])
        action = draft_plan["action"] if approved else "HOLD"
        reasons = list(risk_report["reasons"])

        return {
            **draft_plan,
            "action": action,
            "position_size": risk_report["position_size"],
            "risk_amount": risk_report["risk_amount"],
            "approved": approved,
            "reasons": reasons,
        }

    def _maybe_add_llm_note(
        self,
        *,
        final_plan: dict[str, Any],
        ta_report: dict[str, Any],
        sentiment_report: dict[str, Any],
        risk_report: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.llm_client.enabled:
            return final_plan

        prompt = (
            "Summarize this already-approved trading workflow output in one short sentence.\n"
            f"Plan: {final_plan}\n"
            f"TA: {ta_report}\n"
            f"Sentiment: {sentiment_report}\n"
            f"Risk: {risk_report}"
        )
        constraints = {
            "do_not_change_action": final_plan["action"],
            "do_not_change_approval": final_plan["approved"],
            "max_sentences": 1,
        }
        llm_result = self.llm_client.generate(prompt, constraints=constraints)
        llm_message = str(llm_result.get("message", "")).strip()
        if not llm_message:
            return final_plan

        notes = list(final_plan.get("notes", []))
        notes.append(f"LLM summary: {llm_message}")
        return {**final_plan, "notes": notes}
