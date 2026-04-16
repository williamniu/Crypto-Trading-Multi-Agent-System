from __future__ import annotations

from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.sentiment_analyst.toolset import SentimentAnalystToolset


class SentimentAnalystAgent(BaseAgent):
    """Role-bound sentiment analysis agent."""

    def __init__(self, toolset: SentimentAnalystToolset | None = None) -> None:
        self.toolset = toolset or SentimentAnalystToolset()
        super().__init__(name="sentiment_analyst", tool_registry=self.toolset.registry)

    def run(
        self,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        return self.toolset.generate_report(payload, trace=trace)
