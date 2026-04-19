from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SentimentReport(BaseModel):
	model_config = ConfigDict(extra="forbid")

	symbol: str = Field(min_length=3)
	headline_count: int = Field(ge=0)
	sentiment_score: float = Field(ge=-1, le=1)
	event_impact: Literal["positive", "negative", "neutral"]
	headlines: list[str] = Field(default_factory=list)
	llm_summary: str | None = None
