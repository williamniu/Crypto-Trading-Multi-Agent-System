from __future__ import annotations

from statistics import mean
from typing import Any

from app.agents.base.base_tool import BaseTool


class CalcIndicatorTool(BaseTool):
    """Compute deterministic trend and momentum metrics."""

    def __init__(self) -> None:
        super().__init__(
            name="calc_indicator",
            description="Calculate trend and momentum from OHLCV candles.",
            required_fields=["candles"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        candles = payload["candles"]
        if len(candles) < 3:
            raise ValueError("calc_indicator requires at least 3 candles")

        closes = [float(item["close"]) for item in candles]
        trend = closes[-1] - closes[0]
        momentum = closes[-1] - mean(closes[-3:])
        return {"trend": round(trend, 4), "momentum": round(momentum, 4)}
