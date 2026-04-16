from __future__ import annotations

from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.risk_officer.toolset import RiskOfficerToolset


class RiskOfficerAgent(BaseAgent):
    """Risk gatekeeper for the MVP trading workflow."""

    def __init__(self, toolset: RiskOfficerToolset | None = None) -> None:
        self.toolset = toolset or RiskOfficerToolset()
        super().__init__(name="risk_officer", tool_registry=self.toolset.registry)

    def run(
        self,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        return self.toolset.review_plan(
            task=payload["task"],
            draft_plan=payload["draft_plan"],
            trace=trace,
        )
