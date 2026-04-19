from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool
from app.services.news_service import NewsService


class FetchNewsTool(BaseTool):
    """Fetch deterministic headlines for sentiment analysis."""

    def __init__(self, news_service: NewsService | None = None) -> None:
        super().__init__(
            name="fetch_news",
            description="Fetch mock crypto and macro headlines for a symbol.",
            required_fields=["symbol"],
        )
        self.news_service = news_service or NewsService()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        symbol = str(payload["symbol"]).upper()
        bundle = self.news_service.fetch_news_bundle(symbol=symbol)
        return {
            "provider": bundle.get("provider", "unknown"),
            "headlines": bundle["headlines"],
            "items": bundle.get("items", []),
            "query": bundle.get("query", ""),
        }
