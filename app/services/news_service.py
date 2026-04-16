from __future__ import annotations

from dataclasses import dataclass


_NEWS_BY_SYMBOL: dict[str, list[str]] = {
    "BTCUSDT": [
        "BTC ETF inflow rises for third week",
        "US inflation cools, risk assets supported",
        "Major exchange reports stable reserves",
    ],
    "ETHUSDT": [
        "ETH staking activity rises as fees stabilize",
        "Layer-2 growth supports Ethereum demand",
        "Macro sentiment remains constructive for large-cap crypto",
    ],
    "SOLUSDT": [
        "SOL developer activity improves after outage-free month",
        "DeFi volume on Solana rises on renewed user demand",
        "Risk appetite remains steady across altcoin markets",
    ],
}


@dataclass(frozen=True)
class NewsService:
    """Deterministic mock news source used by the sentiment analyst."""

    def fetch_headlines(self, *, symbol: str) -> list[str]:
        normalized_symbol = symbol.upper()
        return list(
            _NEWS_BY_SYMBOL.get(
                normalized_symbol,
                [
                    f"{normalized_symbol} liquidity improves on calmer macro backdrop",
                    f"{normalized_symbol} market structure remains stable in quiet session",
                    f"{normalized_symbol} traders monitor upcoming catalysts with neutral bias",
                ],
            )
        )
