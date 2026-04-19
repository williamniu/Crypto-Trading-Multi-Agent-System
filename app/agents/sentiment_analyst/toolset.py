from __future__ import annotations

from typing import Any

from app.config.settings import Settings, load_settings
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.services.llm_client import LLMClient
from app.services.news_service import NewsService
from app.agents.sentiment_analyst.tools.classify_event_tool import ClassifyEventTool
from app.agents.sentiment_analyst.tools.fetch_news_tool import FetchNewsTool
from app.agents.sentiment_analyst.tools.score_sentiment_tool import ScoreSentimentTool


class SentimentAnalystToolset:
    """MVP toolset that produces a simple sentiment report."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.llm_client = llm_client or LLMClient(settings=self.settings)
        self.registry = ToolRegistry()
        self.registry.register_many(
            [
                FetchNewsTool(news_service=NewsService(settings=self.settings)),
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

        report = {
            "symbol": task.get("symbol", "BTCUSDT"),
            "headline_count": len(news["headlines"]),
            "sentiment_score": scored["score"],
            "event_impact": event["impact"],
            "headlines": news["headlines"],
        }
        return self._maybe_add_llm_summary(report=report, news=news, trace=trace)

    def _maybe_add_llm_summary(
        self,
        *,
        report: dict[str, Any],
        news: dict[str, Any],
        trace: ExecutionTrace | None,
    ) -> dict[str, Any]:
        if not (self.llm_client.enabled and self.settings.llm_enable_sentiment):
            return report

        payload = {
            "symbol": report["symbol"],
            "provider": news.get("provider", "unknown"),
            "headline_count": report["headline_count"],
            "sentiment_score": report["sentiment_score"],
            "event_impact": report["event_impact"],
            "headlines": report["headlines"],
            "items": news.get("items", []),
        }
        llm_result = self.llm_client.generate(
            "Review the sentiment snapshot and explain the market mood.",
            constraints={
                "do_not_change_sentiment_score": report["sentiment_score"],
                "do_not_change_event_impact": report["event_impact"],
                "max_sentences": 2,
            },
            system_prompt=(
                "You are the sentiment analyst in a constrained trading system. "
                "Use only the provided headlines, source items, sentiment score, and event impact. "
                "Do not invent extra news. Do not override the deterministic sentiment score or impact label. "
                "Return a concise explanation of the current sentiment picture."
            ),
        )
        llm_summary = str(llm_result.get("message", "")).strip()
        if trace is not None:
            trace.add_tool_call(
                agent="sentiment_analyst",
                tool_name="llm_sentiment_analysis",
                payload=payload,
                output={"llm_summary": llm_summary},
            )
        if not llm_summary:
            return report
        return {**report, "llm_summary": llm_summary}
