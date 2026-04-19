from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_csv(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


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
    llm_mode: Literal["stub", "openai_compatible"] = "stub"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_temperature: float = Field(default=0.2, ge=0, le=2)
    market_data_provider: Literal["mock", "weex"] = "mock"
    weex_market_type: Literal["spot", "contract"] = "contract"
    sentiment_provider: Literal["mock", "tavily"] = "mock"
    risk_provider: Literal["mock", "weex"] = "mock"
    weex_contract_base_url: str = "https://api-contract.weex.com"
    weex_spot_base_url: str = "https://api-spot.weex.com"
    weex_api_key: str = ""
    weex_api_secret: str = ""
    weex_api_passphrase: str = ""
    weex_margin_asset: str = "USDT"
    weex_positions_path: str = "/capi/v3/position/allPosition"
    tavily_api_key: str = ""
    tavily_base_url: str = "https://api.tavily.com"
    tavily_topic: Literal["news", "general", "finance"] = "news"
    tavily_search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = "basic"
    tavily_max_results: int = Field(default=5, ge=1, le=20)
    tavily_days: int = Field(default=3, ge=1)
    tavily_include_domains: list[str] = Field(default_factory=list)
    tavily_exclude_domains: list[str] = Field(default_factory=list)


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
        llm_base_url=os.getenv("LLM_BASE_URL", ""),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", ""),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        market_data_provider=os.getenv("MARKET_DATA_PROVIDER", "mock"),
        weex_market_type=os.getenv("WEEX_MARKET_TYPE", "contract"),
        sentiment_provider=os.getenv("SENTIMENT_PROVIDER", "mock"),
        risk_provider=os.getenv("RISK_PROVIDER", "mock"),
        weex_contract_base_url=os.getenv(
            "WEEX_CONTRACT_BASE_URL",
            "https://api-contract.weex.com",
        ),
        weex_spot_base_url=os.getenv(
            "WEEX_SPOT_BASE_URL",
            "https://api-spot.weex.com",
        ),
        weex_api_key=os.getenv("WEEX_API_KEY", ""),
        weex_api_secret=os.getenv("WEEX_API_SECRET", ""),
        weex_api_passphrase=os.getenv("WEEX_API_PASSPHRASE", ""),
        weex_margin_asset=os.getenv("WEEX_MARGIN_ASSET", "USDT"),
        weex_positions_path=os.getenv(
            "WEEX_POSITIONS_PATH",
            "/capi/v3/position/allPosition",
        ),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        tavily_base_url=os.getenv("TAVILY_BASE_URL", "https://api.tavily.com"),
        tavily_topic=os.getenv("TAVILY_TOPIC", "news"),
        tavily_search_depth=os.getenv("TAVILY_SEARCH_DEPTH", "basic"),
        tavily_max_results=int(os.getenv("TAVILY_MAX_RESULTS", "5")),
        tavily_days=int(os.getenv("TAVILY_DAYS", "3")),
        tavily_include_domains=_get_csv("TAVILY_INCLUDE_DOMAINS"),
        tavily_exclude_domains=_get_csv("TAVILY_EXCLUDE_DOMAINS"),
    )
