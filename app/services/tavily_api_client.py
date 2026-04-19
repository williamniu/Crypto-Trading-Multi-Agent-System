from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.http_json_client import HTTPJSONClient


@dataclass(frozen=True)
class TavilyAPIClient:
    """Thin wrapper around Tavily's `/search` endpoint."""

    api_key: str
    base_url: str = "https://api.tavily.com"
    http_client: HTTPJSONClient = HTTPJSONClient()

    def search_news(
        self,
        *,
        query: str,
        max_results: int,
        search_depth: str,
        topic: str,
        days: int,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body: dict[str, Any] = {
            "query": query,
            "topic": topic,
            "search_depth": search_depth,
            "max_results": max_results,
            "days": days,
            "include_answer": False,
            "include_raw_content": False,
        }

        if include_domains:
            body["include_domains"] = include_domains
        if exclude_domains:
            body["exclude_domains"] = exclude_domains

        return self.http_client.request_json(
            method="POST",
            url=f"{self.base_url.rstrip('/')}/search",
            headers=headers,
            body=body,
        )
