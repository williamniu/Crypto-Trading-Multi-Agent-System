from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TAIndicators(BaseModel):
	model_config = ConfigDict(extra="forbid")

	trend: float
	momentum: float


class TALevels(BaseModel):
	model_config = ConfigDict(extra="forbid")

	support: float
	resistance: float

	@model_validator(mode="after")
	def validate_range(self) -> "TALevels":
		if self.support > self.resistance:
			raise ValueError("support must be less than or equal to resistance")
		return self


class TAReport(BaseModel):
	model_config = ConfigDict(extra="forbid")

	symbol: str = Field(min_length=3)
	timeframe: Literal["15m", "1h", "4h", "1d"]
	signal: Literal["bullish", "bearish", "neutral"]
	confidence: float = Field(ge=0, le=1)
	indicators: TAIndicators
	levels: TALevels
	llm_summary: str | None = None
