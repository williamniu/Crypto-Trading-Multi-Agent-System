from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_DEFAULT_RISK_PROFILE = {
    "account_balance": 10_000.0,
    "risk_per_trade": 0.01,
    "current_exposure": 0.10,
    "max_exposure": 0.30,
}


@dataclass(frozen=True)
class RiskService:
    """Normalizes risk inputs before risk tools apply explicit policies."""

    def normalize_profile(self, risk_payload: dict[str, Any] | None) -> dict[str, float]:
        merged = {**_DEFAULT_RISK_PROFILE, **(risk_payload or {})}
        profile = {key: float(value) for key, value in merged.items()}

        if profile["account_balance"] <= 0:
            raise ValueError("account_balance must be positive")
        if not 0 < profile["risk_per_trade"] <= 1:
            raise ValueError("risk_per_trade must be between 0 and 1")
        if not 0 <= profile["current_exposure"] <= 1:
            raise ValueError("current_exposure must be between 0 and 1")
        if not 0 < profile["max_exposure"] <= 1:
            raise ValueError("max_exposure must be between 0 and 1")

        return profile
