from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings, load_settings
from app.services.tavily_api_client import TavilyAPIClient


_NEWS_BY_SYMBOL: dict[str, list[str]] = {
    "BTCUSDT": [
        "BTC ETF inflow rises for third week",
        "US inflation cools, risk assets supported",
        "Major exchange reports stable reserves",
    ],
    "ETHUSDT": [
        "ETH staking activity rises as fees stabilize",
        "Layer-2 growth supports Ethereum demand",
        "Macro sentiment remains constructive for large-cap crypto",
    ],
    "SOLUSDT": [
        "SOL developer activity improves after outage-free month",
        "DeFi volume on Solana rises on renewed user demand",
        "Risk appetite remains steady across altcoin markets",
    ],
}


@dataclass(frozen=True)
class NewsService:
    """Sentiment news facade with mock and Tavily-backed implementations."""

    settings: Settings | None = None
    tavily_client: TavilyAPIClient | None = None

    def __post_init__(self) -> None:
        resolved_settings = self.settings or load_settings()
        object.__setattr__(self, "settings", resolved_settings)
        if self.tavily_client is None and resolved_settings.tavily_api_key:
            object.__setattr__(
                self,
                "tavily_client",
                TavilyAPIClient(
                    api_key=resolved_settings.tavily_api_key,
                    base_url=resolved_settings.tavily_base_url,
                ),
            )

    def fetch_headlines(self, *, symbol: str) -> list[str]:
        return self.fetch_news_bundle(symbol=symbol)["headlines"]

    def fetch_news_bundle(self, *, symbol: str) -> dict[str, Any]:
        normalized_symbol = symbol.upper()
        if self.settings.sentiment_provider == "tavily":
            return self._fetch_tavily_news(symbol=normalized_symbol)
        return self._fetch_mock_news(symbol=normalized_symbol)

    def _fetch_mock_news(self, *, symbol: str) -> dict[str, Any]:
        headlines = list(
            _NEWS_BY_SYMBOL.get(
                symbol,
                [
                    f"{symbol} liquidity improves on calmer macro backdrop",
                    f"{symbol} market structure remains stable in quiet session",
                    f"{symbol} traders monitor upcoming catalysts with neutral bias",
                ],
            )
        )
        return {
            "provider": "mock",
            "headlines": headlines,
            "items": [{"title": title, "url": "", "source": "mock"} for title in headlines],
        }

    def _fetch_tavily_news(self, *, symbol: str) -> dict[str, Any]:
        if self.tavily_client is None:
            raise ValueError("Tavily API key is required when sentiment_provider=tavily")

        response = self.tavily_client.search_news(
            query=f"{symbol} crypto market news",
            max_results=self.settings.tavily_max_results,
            search_depth=self.settings.tavily_search_depth,
            topic=self.settings.tavily_topic,
            days=self.settings.tavily_days,
            include_domains=self.settings.tavily_include_domains,
            exclude_domains=self.settings.tavily_exclude_domains,
        )

        items: list[dict[str, Any]] = []
        headlines: list[str] = []
        seen_titles: set[str] = set()

        for result in response.get("results", []):
            title = str(result.get("title") or result.get("url") or "").strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            headlines.append(title)
            items.append(
                {
                    "title": title,
                    "url": str(result.get("url", "")),
                    "source": str(result.get("source", "")),
                    "published_date": str(
                        result.get("published_date") or result.get("publishedAt") or ""
                    ),
                    "content": str(result.get("content", "")),
                    "score": result.get("score"),
                }
            )

        return {
            "provider": "tavily",
            "headlines": headlines,
            "items": items,
            "query": response.get("query", f"{symbol} crypto market news"),
        }
