from __future__ import annotations

import string
from typing import Any

from app.agents.base.base_tool import BaseTool


_POSITIVE_WORDS = {"rise", "rises", "supported", "stable", "inflow", "improves", "growth"}
_NEGATIVE_WORDS = {"ban", "hack", "lawsuit", "liquidation", "outflow", "outage"}


class ScoreSentimentTool(BaseTool):
    """Score headline sentiment using a deterministic keyword model."""

    def __init__(self) -> None:
        super().__init__(
            name="score_sentiment",
            description="Score sentiment from a list of headlines.",
            required_fields=["headlines"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        headlines = payload["headlines"]
        if not isinstance(headlines, list):
            raise ValueError("headlines must be a list of strings")

        score = 0
        for text in headlines:
            tokens = {
                token.strip(string.punctuation)
                for token in str(text).lower().split()
            }
            score += sum(1 for word in _POSITIVE_WORDS if word in tokens)
            score -= sum(1 for word in _NEGATIVE_WORDS if word in tokens)

        normalized = max(-1.0, min(1.0, score / 5))
        return {"score": round(normalized, 2)}
