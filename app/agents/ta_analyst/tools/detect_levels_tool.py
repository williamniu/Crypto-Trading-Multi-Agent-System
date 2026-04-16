from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool


class DetectLevelsTool(BaseTool):
    """Find simple support and resistance from close prices."""

    def __init__(self) -> None:
        super().__init__(
            name="detect_levels",
            description="Detect support and resistance from recent candles.",
            required_fields=["candles"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        candles = payload["candles"]
        if not candles:
            raise ValueError("detect_levels requires at least 1 candle")

        closes = [float(item["close"]) for item in candles]
        return {
            "support": round(min(closes), 4),
            "resistance": round(max(closes), 4),
        }
