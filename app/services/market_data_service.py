from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings, load_settings
from app.services.weex_api_client import WEEXAPIClient


_BASE_CLOSES: dict[str, list[float]] = {
    "BTCUSDT": [100.0, 101.5, 102.8, 101.9, 103.2, 104.0],
    "ETHUSDT": [80.0, 80.8, 81.4, 81.1, 82.0, 82.6],
    "SOLUSDT": [60.0, 60.7, 61.3, 61.0, 61.9, 62.4],
}

_TIMEFRAME_DRIFT = {
    "15m": 0.15,
    "1h": 0.25,
    "4h": 0.45,
    "1d": 0.75,
}


@dataclass(frozen=True)
class MarketDataService:
    """Market data facade with mock and WEEX-backed implementations."""

    settings: Settings | None = None
    weex_client: WEEXAPIClient | None = None

    def __post_init__(self) -> None:
        resolved_settings = self.settings or load_settings()
        object.__setattr__(self, "settings", resolved_settings)
        if self.weex_client is None:
            object.__setattr__(
                self,
                "weex_client",
                WEEXAPIClient(
                    contract_base_url=resolved_settings.weex_contract_base_url,
                    spot_base_url=resolved_settings.weex_spot_base_url,
                    api_key=resolved_settings.weex_api_key,
                    api_secret=resolved_settings.weex_api_secret,
                    api_passphrase=resolved_settings.weex_api_passphrase,
                ),
            )

    def get_ohlcv(
        self,
        *,
        symbol: str,
        timeframe: str,
        limit: int = 6,
    ) -> list[dict[str, float]]:
        if self.settings.market_data_provider == "weex":
            return self._get_weex_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        return self._get_mock_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)

    def _get_weex_ohlcv(
        self,
        *,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[dict[str, float]]:
        if self.settings.weex_market_type == "spot":
            raw_klines = self.weex_client.get_spot_klines(
                symbol=symbol.upper(),
                interval=timeframe,
                limit=limit,
            )
        else:
            raw_klines = self.weex_client.get_contract_klines(
                symbol=symbol.upper(),
                interval=timeframe,
                limit=limit,
            )

        klines = raw_klines.get("data", raw_klines) if isinstance(raw_klines, dict) else raw_klines
        candles: list[dict[str, float]] = []
        for item in klines[:limit]:
            candles.append(
                {
                    "open_time": float(item[0]),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                    "close_time": float(item[6]),
                }
            )
        return candles

    def _get_mock_ohlcv(
        self,
        *,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[dict[str, float]]:
        if limit < 3:
            raise ValueError("limit must be at least 3 for indicator calculation")

        closes = self._build_closes(symbol=symbol.upper(), timeframe=timeframe, limit=limit)
        drift = _TIMEFRAME_DRIFT.get(timeframe, 0.25)
        candles: list[dict[str, float]] = []

        for index, close in enumerate(closes):
            open_price = round(close - 0.35 + index * 0.02, 2)
            high = round(close + drift, 2)
            low = round(close - drift, 2)
            volume = float(1_000 + index * 40 + len(symbol) * 5)
            candles.append(
                {
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": round(close, 2),
                    "volume": volume,
                }
            )
        return candles

    def _build_closes(self, *, symbol: str, timeframe: str, limit: int) -> list[float]:
        template = _BASE_CLOSES.get(symbol)
        if template is None:
            seed = sum(ord(char) for char in symbol) % 20
            template = [50.0 + seed + offset for offset in (0.0, 0.8, 1.4, 1.1, 2.0, 2.6)]

        drift = _TIMEFRAME_DRIFT.get(timeframe, 0.25)
        return [round(price + drift * index, 2) for index, price in enumerate(template[:limit])]
