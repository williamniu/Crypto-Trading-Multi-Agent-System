from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool
from app.agents.sentiment_analyst.decision_policy import classify_event_impact


class ClassifyEventTool(BaseTool):
    """Map a normalized sentiment score into event impact buckets."""

    def __init__(self) -> None:
        super().__init__(
            name="classify_event",
            description="Classify the expected market impact from a sentiment score.",
            required_fields=["score"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        score = float(payload["score"])
        return {"impact": classify_event_impact(score)}
