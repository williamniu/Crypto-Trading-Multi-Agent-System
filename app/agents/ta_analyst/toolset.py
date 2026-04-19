from __future__ import annotations

from typing import Any

from app.config.settings import Settings, load_settings
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry
from app.agents.ta_analyst.decision_policy import (
    determine_confidence,
    determine_signal,
)
from app.services.llm_client import LLMClient
from app.services.market_data_service import MarketDataService
from app.agents.ta_analyst.tools.calc_indicator_tool import CalcIndicatorTool
from app.agents.ta_analyst.tools.detect_levels_tool import DetectLevelsTool
from app.agents.ta_analyst.tools.get_ohlcv_tool import GetOHLCVTool


class TAAnalystToolset:
    """MVP toolset that produces a simple technical analysis report."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.llm_client = llm_client or LLMClient(settings=self.settings)
        self.registry = ToolRegistry()
        self.registry.register_many(
            [
                GetOHLCVTool(market_data_service=MarketDataService(settings=self.settings)),
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
        report = {
            "symbol": ohlcv["symbol"],
            "timeframe": ohlcv["timeframe"],
            "signal": signal,
            "confidence": confidence,
            "indicators": indicators,
            "levels": levels,
        }
        return self._maybe_add_llm_summary(
            report=report,
            candles=ohlcv["candles"],
            trace=trace,
        )

    def _maybe_add_llm_summary(
        self,
        *,
        report: dict[str, Any],
        candles: list[dict[str, Any]],
        trace: ExecutionTrace | None,
    ) -> dict[str, Any]:
        if not (self.llm_client.enabled and self.settings.llm_enable_ta):
            return report

        payload = {
            "symbol": report["symbol"],
            "timeframe": report["timeframe"],
            "signal": report["signal"],
            "confidence": report["confidence"],
            "indicators": report["indicators"],
            "levels": report["levels"],
            "recent_candles": candles[-5:],
        }
        llm_result = self.llm_client.generate(
            "Review the TA snapshot and provide a concise analyst-style explanation.",
            constraints={
                "do_not_change_signal": report["signal"],
                "do_not_change_confidence": report["confidence"],
                "max_sentences": 2,
            },
            system_prompt=(
                "You are the technical analyst in a constrained trading system. "
                "Use only the provided candles, indicators, levels, signal, and confidence. "
                "Do not invent missing indicators. Do not override the deterministic signal. "
                "Return a concise explanation of what the current TA picture means."
            ),
        )
        llm_summary = str(llm_result.get("message", "")).strip()
        if trace is not None:
            trace.add_tool_call(
                agent="ta_analyst",
                tool_name="llm_ta_analysis",
                payload=payload,
                output={"llm_summary": llm_summary},
            )
        if not llm_summary:
            return report
        return {**report, "llm_summary": llm_summary}
