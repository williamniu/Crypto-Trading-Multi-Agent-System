from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config.settings import Settings, load_settings
from app.services.weex_api_client import WEEXAPIClient


_DEFAULT_RISK_PROFILE = {
    "account_balance": 10_000.0,
    "risk_per_trade": 0.01,
    "current_exposure": 0.10,
    "max_exposure": 0.30,
}


@dataclass(frozen=True)
class RiskService:
    """Normalizes risk inputs from mock defaults or a live WEEX account snapshot."""

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

    def normalize_profile(self, risk_payload: dict[str, Any] | None) -> dict[str, float]:
        if self.settings.risk_provider == "weex":
            merged = self._merge_live_profile(risk_payload)
        else:
            merged = self._merge_mock_profile(risk_payload)

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

    def _merge_mock_profile(self, risk_payload: dict[str, Any] | None) -> dict[str, float]:
        payload = {key: value for key, value in (risk_payload or {}).items() if value is not None}
        return {**_DEFAULT_RISK_PROFILE, **payload}

    def _merge_live_profile(self, risk_payload: dict[str, Any] | None) -> dict[str, float]:
        payload = {key: value for key, value in (risk_payload or {}).items() if value is not None}
        live_profile = self._fetch_weex_profile()
        merged = {
            "account_balance": live_profile["account_balance"],
            "risk_per_trade": self.settings.default_risk_per_trade,
            "current_exposure": live_profile["current_exposure"],
            "max_exposure": self.settings.default_max_exposure,
        }
        return {**merged, **payload}

    def _fetch_weex_profile(self) -> dict[str, float]:
        assets_response = self.weex_client.get_contract_account_assets()
        positions_response = self.weex_client.get_contract_positions(
            path=self.settings.weex_positions_path
        )
        assets = (
            assets_response.get("data", assets_response)
            if isinstance(assets_response, dict)
            else assets_response
        )
        positions = (
            positions_response.get("data", positions_response)
            if isinstance(positions_response, dict)
            else positions_response
        )

        margin_asset = self.settings.weex_margin_asset.upper()
        asset_row = next(
            (
                item
                for item in assets
                if str(item.get("coinName", item.get("asset", ""))).upper() == margin_asset
            ),
            None,
        )
        if asset_row is None:
            raise ValueError(f"WEEX account asset snapshot missing margin asset {margin_asset}")

        equity = float(asset_row.get("equity") or asset_row.get("free") or 0.0)
        if equity <= 0:
            raise ValueError("WEEX account equity must be positive")

        open_notional = 0.0
        for position in positions:
            symbol = str(position.get("symbol", "")).upper()
            if not symbol:
                continue
            open_notional += abs(
                float(
                    position.get("openValue")
                    or position.get("positionValue")
                    or position.get("notional")
                    or 0.0
                )
            )

        current_exposure = min(1.0, open_notional / equity) if equity else 0.0
        return {
            "account_balance": round(equity, 8),
            "current_exposure": round(current_exposure, 8),
        }
