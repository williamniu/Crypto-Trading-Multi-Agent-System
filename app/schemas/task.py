from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskInput(BaseModel):
	model_config = ConfigDict(extra="forbid")

	account_balance: float = Field(gt=0)
	risk_per_trade: float = Field(gt=0, le=1)
	current_exposure: float = Field(ge=0, le=1)
	max_exposure: float = Field(gt=0, le=1)


class Task(BaseModel):
	model_config = ConfigDict(extra="forbid")

	task_id: str = Field(min_length=1)
	symbol: str = Field(min_length=3)
	timeframe: Literal["15m", "1h", "4h", "1d"] = "1h"
	objective: str = "analyze_trade_setup"
	risk: RiskInput
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))