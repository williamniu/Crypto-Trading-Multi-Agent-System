from __future__ import annotations

from typing import Any

from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.agents.ta_analyst.decision_policy import (
    determine_confidence,
    determine_signal,
)
from app.agents.ta_analyst.tools.calc_indicator_tool import CalcIndicatorTool
from app.agents.ta_analyst.tools.detect_levels_tool import DetectLevelsTool
from app.agents.ta_analyst.tools.get_ohlcv_tool import GetOHLCVTool


class TAAnalystToolset:
    """MVP toolset that produces a simple technical analysis report."""

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.registry.register_many(
            [
                GetOHLCVTool(),
                CalcIndicatorTool(),
                DetectLevelsTool(),
            ]
        )

    def generate_report(
        self,
        task: dict[str, Any],
        trace: ExecutionTrace | None = None,
    ) -> dict[str, Any]:
        ohlcv = self.registry.execute(
            tool_name="get_ohlcv",
            payload={
                "symbol": task.get("symbol", "BTCUSDT"),
                "timeframe": task.get("timeframe", "1h"),
            },
            trace=trace,
            agent_name="ta_analyst",
        )
        indicators = self.registry.execute(
            tool_name="calc_indicator",
            payload={"candles": ohlcv["candles"]},
            trace=trace,
            agent_name="ta_analyst",
        )
        levels = self.registry.execute(
            tool_name="detect_levels",
            payload={"candles": ohlcv["candles"]},
            trace=trace,
            agent_name="ta_analyst",
        )

        signal = determine_signal(
            trend=indicators["trend"],
            momentum=indicators["momentum"],
        )
        confidence = determine_confidence(
            trend=indicators["trend"],
            momentum=indicators["momentum"],
            signal=signal,
        )
        return {
            "symbol": ohlcv["symbol"],
            "timeframe": ohlcv["timeframe"],
            "signal": signal,
            "confidence": confidence,
            "indicators": indicators,
            "levels": levels,
        }
