from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry


class BaseAgent(ABC):
    """Base contract for all role-specific agents."""

    def __init__(
        self,
        name: str,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.name = name
        self.tool_registry = tool_registry or ToolRegistry()

    def run_tool(
        self,
        tool_name: str,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        return self.tool_registry.execute(
            tool_name=tool_name,
            payload=payload,
            trace=trace,
            agent_name=self.name,
        )

    @abstractmethod
    def run(
        self,
        payload: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        """Run agent reasoning and return a report-like dict."""

    def result(self, **kwargs: Any) -> dict[str, Any]:
        return {"agent": self.name, **kwargs}
