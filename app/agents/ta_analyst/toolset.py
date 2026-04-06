from __future__ import annotations

from statistics import mean
from typing import Any

from app.agents.base.base_tool import FunctionTool
from app.agents.base.execution_trace import ExecutionTrace
from app.agents.base.tool_registry import ToolRegistry


class TAAnalystToolset:
	"""MVP toolset that produces a simple technical analysis report."""

	def __init__(self) -> None:
		self.registry = ToolRegistry()
		self.registry.register_many(
			[
				FunctionTool(
					name="get_ohlcv",
					description="Fetch mock OHLCV candles.",
					required_fields=["symbol", "timeframe"],
					handler=self._get_ohlcv,
				),
				FunctionTool(
					name="calc_indicator",
					description="Calculate trend and momentum values.",
					required_fields=["candles"],
					handler=self._calc_indicator,
				),
				FunctionTool(
					name="detect_levels",
					description="Find support/resistance levels.",
					required_fields=["candles"],
					handler=self._detect_levels,
				),
			]
		)

	@staticmethod
	def _get_ohlcv(payload: dict[str, Any]) -> dict[str, Any]:
		symbol = payload["symbol"]
		timeframe = payload["timeframe"]
		closes = [100.0, 101.5, 102.8, 101.9, 103.2, 104.0]
		candles = [{"close": close, "volume": 1000 + idx * 40} for idx, close in enumerate(closes)]
		return {"symbol": symbol, "timeframe": timeframe, "candles": candles}

	@staticmethod
	def _calc_indicator(payload: dict[str, Any]) -> dict[str, Any]:
		candles = payload["candles"]
		closes = [item["close"] for item in candles]
		trend = closes[-1] - closes[0]
		momentum = closes[-1] - mean(closes[-3:])
		return {"trend": round(trend, 4), "momentum": round(momentum, 4)}

	@staticmethod
	def _detect_levels(payload: dict[str, Any]) -> dict[str, Any]:
		closes = [item["close"] for item in payload["candles"]]
		return {"support": min(closes), "resistance": max(closes)}

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

		signal = "bullish" if indicators["trend"] >= 0 else "bearish"
		confidence = min(0.95, max(0.5, 0.5 + abs(indicators["momentum"]) / 10))
		return {
			"symbol": ohlcv["symbol"],
			"timeframe": ohlcv["timeframe"],
			"signal": signal,
			"confidence": round(confidence, 2),
			"indicators": indicators,
			"levels": levels,
		}
