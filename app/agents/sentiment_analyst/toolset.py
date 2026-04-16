from __future__ import annotations

from typing import Any

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.agents.sentiment_analyst.tools.classify_event_tool import ClassifyEventTool
from app.agents.sentiment_analyst.tools.fetch_news_tool import FetchNewsTool
from app.agents.sentiment_analyst.tools.score_sentiment_tool import ScoreSentimentTool


class SentimentAnalystToolset:
    """MVP toolset that produces a simple sentiment report."""

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register_many(
            [
                FetchNewsTool(),
                ScoreSentimentTool(),
                ClassifyEventTool(),
            ]
        )

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
