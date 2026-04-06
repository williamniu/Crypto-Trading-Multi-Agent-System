from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import FunctionTool
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry


class SentimentAnalystToolset:
	"""MVP toolset that produces a simple sentiment report."""

	def __init__(self) -> None:
		self.registry = ToolRegistry()
		self.registry.register_many(
			[
				FunctionTool(
					name="fetch_news",
					description="Fetch mock crypto/macro headlines.",
					required_fields=["symbol"],
					handler=self._fetch_news,
				),
				FunctionTool(
					name="score_sentiment",
					description="Score sentiment from headlines.",
					required_fields=["headlines"],
					handler=self._score_sentiment,
				),
				FunctionTool(
					name="classify_event",
					description="Classify expected market impact.",
					required_fields=["score"],
					handler=self._classify_event,
				),
			]
		)

	@staticmethod
	def _fetch_news(payload: dict[str, Any]) -> dict[str, Any]:
		symbol = payload["symbol"]
		headlines = [
			f"{symbol} ETF inflow rises for third week",
			"US inflation cools, risk assets supported",
			"Major exchange reports stable reserves",
		]
		return {"headlines": headlines}

	@staticmethod
	def _score_sentiment(payload: dict[str, Any]) -> dict[str, Any]:
		positive_words = {"rise", "rises", "supported", "stable", "inflow"}
		negative_words = {"ban", "hack", "lawsuit", "liquidation", "outflow"}

		score = 0
		for text in payload["headlines"]:
			lowered = text.lower()
			score += sum(1 for word in positive_words if word in lowered)
			score -= sum(1 for word in negative_words if word in lowered)
		normalized = max(-1.0, min(1.0, score / 5))
		return {"score": round(normalized, 2)}

	@staticmethod
	def _classify_event(payload: dict[str, Any]) -> dict[str, Any]:
		score = payload["score"]
		if score >= 0.4:
			impact = "positive"
		elif score <= -0.4:
			impact = "negative"
		else:
			impact = "neutral"
		return {"impact": impact}

	def generate_report(
		self,
		task: dict[str, Any],
		trace: ExecutionTrace | None = None,
	) -> dict[str, Any]:
		news = self.registry.execute(
			tool_name="fetch_news",
			payload={"symbol": task.get("symbol", "BTCUSDT")},
			trace=trace,
			agent_name="sentiment_analyst",
		)
		scored = self.registry.execute(
			tool_name="score_sentiment",
			payload={"headlines": news["headlines"]},
			trace=trace,
			agent_name="sentiment_analyst",
		)
		event = self.registry.execute(
			tool_name="classify_event",
			payload={"score": scored["score"]},
			trace=trace,
			agent_name="sentiment_analyst",
		)

		return {
			"symbol": task.get("symbol", "BTCUSDT"),
			"headline_count": len(news["headlines"]),
			"sentiment_score": scored["score"],
			"event_impact": event["impact"],
			"headlines": news["headlines"],
		}
