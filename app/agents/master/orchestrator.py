from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.master.agent import MasterAgent


class MasterOrchestrator:
    """Coordinates role agents into a traceable final trade plan."""

    def __init__(self, master_agent: MasterAgent | None = None) -> None:
        self.master_agent = master_agent or MasterAgent()

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        trace = ExecutionTrace(run_id=str(uuid4()))
        trace.add_stage("start")

        try:
            result = self.master_agent.run(task, trace=trace)
            trace.add_stage("complete")
        except Exception:
            trace.add_stage("failed")
            trace.complete()
            raise

        trace.complete()
        return {**result, "trace": trace.to_dict()}
