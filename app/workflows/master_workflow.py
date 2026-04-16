from __future__ import annotations

from typing import Any

from app.agents.master.orchestrator import MasterOrchestrator
from app.config.settings import Settings, load_settings
from app.schemas.risk_report import RiskReport
from app.schemas.sentiment_report import SentimentReport
from app.schemas.ta_report import TAReport
from app.schemas.task import Task
from app.schemas.trade_plan import TradePlan
from app.services.storage_service import StorageService


class MasterWorkflow:
    """Top-level workflow that validates inputs and outputs for the MVP."""

    def __init__(
        self,
        orchestrator: MasterOrchestrator | None = None,
        settings: Settings | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.orchestrator = orchestrator or MasterOrchestrator()
        self.storage_service = storage_service or StorageService(
            base_dir=self.settings.audit_dir
        )

    def run(self, task: Task | dict[str, Any]) -> dict[str, Any]:
        validated_task = Task.model_validate(task)
        task_payload = validated_task.model_dump(mode="json")
        result = self.orchestrator.run(task_payload)

        result["task"] = task_payload
        result["ta_report"] = TAReport.model_validate(result["ta_report"]).model_dump()
        result["sentiment_report"] = SentimentReport.model_validate(
            result["sentiment_report"]
        ).model_dump()
        result["risk_report"] = RiskReport.model_validate(result["risk_report"]).model_dump()
        result["trade_plan"] = TradePlan.model_validate(result["trade_plan"]).model_dump()

        if self.settings.enable_audit_persistence:
            self._persist_artifacts(result)

        return result

    def _persist_artifacts(self, result: dict[str, Any]) -> None:
        run_id = result["trace"]["run_id"]
        self.storage_service.write_json(f"agent_runs/{run_id}.json", result["trace"])
        self.storage_service.write_json(
            f"trade_plans/{run_id}.json",
            result["trade_plan"],
        )
