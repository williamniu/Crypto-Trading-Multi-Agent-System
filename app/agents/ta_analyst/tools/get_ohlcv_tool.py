from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool
from app.services.market_data_service import MarketDataService


class GetOHLCVTool(BaseTool):
    """Fetch deterministic mock OHLCV candles for TA analysis."""

    def __init__(self, market_data_service: MarketDataService | None = None) -> None:
        super().__init__(
            name="get_ohlcv",
            description="Fetch mock OHLCV candles for a symbol and timeframe.",
            required_fields=["symbol", "timeframe"],
        )
        self.market_data_service = market_data_service or MarketDataService()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        symbol = str(payload["symbol"]).upper()
        timeframe = str(payload["timeframe"])
        candles = self.market_data_service.get_ohlcv(symbol=symbol, timeframe=timeframe)
        return {"symbol": symbol, "timeframe": timeframe, "candles": candles}
