from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
	return datetime.now(timezone.utc).isoformat()


@dataclass
class ToolCallTrace:
	agent: str
	tool_name: str
	payload: dict[str, Any]
	output: dict[str, Any]
	started_at: str = field(default_factory=_utc_now)
	finished_at: str = field(default_factory=_utc_now)


@dataclass
class ExecutionTrace:
	run_id: str
	started_at: str = field(default_factory=_utc_now)
	finished_at: str | None = None
	stages: list[str] = field(default_factory=list)
	tool_calls: list[ToolCallTrace] = field(default_factory=list)

	def add_stage(self, stage: str) -> None:
		self.stages.append(stage)

	def add_tool_call(
		self,
		*,
		agent: str,
		tool_name: str,
		payload: dict[str, Any],
		output: dict[str, Any],
	) -> None:
		self.tool_calls.append(
			ToolCallTrace(
				agent=agent,
				tool_name=tool_name,
				payload=payload,
				output=output,
			)
		)

	def complete(self) -> None:
		self.finished_at = _utc_now()

	def to_dict(self) -> dict[str, Any]:
		return {
			"run_id": self.run_id,
			"started_at": self.started_at,
			"finished_at": self.finished_at,
			"stages": self.stages,
			"tool_calls": [asdict(item) for item in self.tool_calls],
		}
