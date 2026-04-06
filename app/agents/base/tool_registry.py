from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool
from app.agents.base.execution_trace import ExecutionTrace


class ToolRegistry:
	"""Simple in-memory tool registry for agent runtime."""

	def __init__(self) -> None:
		self._tools: dict[str, BaseTool] = {}

	def register(self, tool: BaseTool) -> None:
		if tool.name in self._tools:
			raise ValueError(f"Tool already registered: {tool.name}")
		self._tools[tool.name] = tool

	def register_many(self, tools: list[BaseTool]) -> None:
		for tool in tools:
			self.register(tool)

	def get(self, tool_name: str) -> BaseTool:
		try:
			return self._tools[tool_name]
		except KeyError as error:
			raise KeyError(f"Tool not found: {tool_name}") from error

	def has(self, tool_name: str) -> bool:
		return tool_name in self._tools

	def list_tools(self) -> list[str]:
		return sorted(self._tools.keys())

	def execute(
		self,
		*,
		tool_name: str,
		payload: dict[str, Any],
		trace: ExecutionTrace | None = None,
		agent_name: str = "unknown",
	) -> dict[str, Any]:
		tool = self.get(tool_name)
		output = tool(payload)
		if trace is not None:
			trace.add_tool_call(
				agent=agent_name,
				tool_name=tool_name,
				payload=payload,
				output=output,
			)
		return output
