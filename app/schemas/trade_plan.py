from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TradePlan(BaseModel):
	model_config = ConfigDict(extra="forbid")

	task_id: str | None = None
	symbol: str = Field(min_length=3)
	action: Literal["BUY", "SELL", "HOLD"]
	confidence: float = Field(ge=0, le=1)
	combined_score: float = Field(ge=-1, le=1)
	entry_hint: str = "market"
	stop_loss_pct: float = Field(gt=0, lt=1)
	take_profit_pct: float = Field(gt=0, lt=1)
	rr_ratio: float = Field(gt=0)
	target_exposure: float = Field(ge=0, le=1)
	position_size: float = Field(gt=0)
	risk_amount: float = Field(ge=0)
	approved: bool
	reasons: list[str] = Field(default_factory=list)
	notes: list[str] = Field(default_factory=list)
	ta_signal: Literal["bullish", "bearish", "neutral"]
	sentiment_score: float = Field(ge=-1, le=1)

	@model_validator(mode="after")
	def validate_percentages(self) -> "TradePlan":
		if self.take_profit_pct <= self.stop_loss_pct:
			raise ValueError("take_profit_pct must be greater than stop_loss_pct")
		if not self.approved and self.action != "HOLD":
			raise ValueError("unapproved plans must use HOLD action")
		return self
