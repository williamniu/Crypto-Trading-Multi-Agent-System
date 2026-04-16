from __future__ import annotations

from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.ta_analyst.toolset import TAAnalystToolset


class TAAnalystAgent(BaseAgent):
    """Role-bound technical analysis agent."""

    def __init__(self, toolset: TAAnalystToolset | None = None) -> None:
        self.toolset = toolset or TAAnalystToolset()
        super().__init__(name="ta_analyst", tool_registry=self.toolset.registry)

    def run(
        self,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        return self.toolset.generate_report(payload, trace=trace)
