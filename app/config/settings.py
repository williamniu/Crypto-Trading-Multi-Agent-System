from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    """Centralized runtime settings for the deterministic MVP."""

    model_config = ConfigDict(extra="forbid")

    app_name: str = "crypto-trading-mas"
    environment: Literal["local", "test", "dev", "prod"] = "local"
    default_symbol: str = "BTCUSDT"
    default_timeframe: Literal["15m", "1h", "4h", "1d"] = "1h"
    default_account_balance: float = Field(default=10_000.0, gt=0)
    default_risk_per_trade: float = Field(default=0.01, gt=0, le=1)
    default_current_exposure: float = Field(default=0.10, ge=0, le=1)
    default_max_exposure: float = Field(default=0.30, gt=0, le=1)
    default_target_exposure: float = Field(default=0.05, ge=0, le=1)
    enable_audit_persistence: bool = False
    audit_dir: str = "app/audits"
    llm_mode: Literal["stub"] = "stub"


def load_settings() -> Settings:
    """Load settings from environment with safe local defaults."""

    return Settings(
        app_name=os.getenv("APP_NAME", "crypto-trading-mas"),
        environment=os.getenv("APP_ENV", "local"),
        default_symbol=os.getenv("DEFAULT_SYMBOL", "BTCUSDT"),
        default_timeframe=os.getenv("DEFAULT_TIMEFRAME", "1h"),
        default_account_balance=float(
            os.getenv("DEFAULT_ACCOUNT_BALANCE", "10000")
        ),
        default_risk_per_trade=float(os.getenv("DEFAULT_RISK_PER_TRADE", "0.01")),
        default_current_exposure=float(
            os.getenv("DEFAULT_CURRENT_EXPOSURE", "0.10")
        ),
        default_max_exposure=float(os.getenv("DEFAULT_MAX_EXPOSURE", "0.30")),
        default_target_exposure=float(
            os.getenv("DEFAULT_TARGET_EXPOSURE", "0.05")
        ),
        enable_audit_persistence=_get_bool("ENABLE_AUDIT_PERSISTENCE", False),
        audit_dir=os.getenv("AUDIT_DIR", "app/audits"),
        llm_mode=os.getenv("LLM_MODE", "stub"),
    )
