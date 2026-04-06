from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RiskReport(BaseModel):
	model_config = ConfigDict(extra="forbid")

	position_size: float = Field(gt=0)
	risk_amount: float = Field(ge=0)
	total_exposure: float = Field(ge=0)
	exposure_ok: bool
	approved: bool
	reasons: list[str] = Field(default_factory=list)
