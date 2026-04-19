from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from app.services.http_json_client import HTTPJSONClient


@dataclass(frozen=True)
class WEEXAPIClient:
    """WEEX REST client for public market data and private account reads."""

    contract_base_url: str = "https://api-contract.weex.com"
    spot_base_url: str = "https://api-spot.weex.com"
    api_key: str = ""
    api_secret: str = ""
    api_passphrase: str = ""
    locale: str = "en-US"
    http_client: HTTPJSONClient = HTTPJSONClient()

    def get_contract_klines(
        self,
        *,
        symbol: str,
        interval: str,
        limit: int,
    ) -> list[list[Any]]:
        return self._request_public(
            base_url=self.contract_base_url,
            path="/capi/v3/market/klines",
            query={"symbol": symbol, "interval": interval, "limit": limit},
        )

    def get_spot_klines(
        self,
        *,
        symbol: str,
        interval: str,
        limit: int,
    ) -> list[list[Any]]:
        return self._request_public(
            base_url=self.spot_base_url,
            path="/api/v3/market/klines",
            query={"symbol": symbol, "interval": interval, "limit": limit},
        )

    def get_contract_account_assets(self) -> list[dict[str, Any]]:
        return self._request_private(
            base_url=self.contract_base_url,
            path="/capi/v2/account/assets",
        )

    def get_contract_positions(self, *, path: str) -> list[dict[str, Any]]:
        return self._request_private(
            base_url=self.contract_base_url,
            path=path,
        )

    def _request_public(
        self,
        *,
        base_url: str,
        path: str,
        query: dict[str, Any] | None = None,
    ) -> Any:
        query_string = urlencode(query or {})
        url = f"{base_url.rstrip('/')}{path}"
        if query_string:
            url = f"{url}?{query_string}"
        return self.http_client.request_json(method="GET", url=url)

    def _request_private(
        self,
        *,
        base_url: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        if not (self.api_key and self.api_secret and self.api_passphrase):
            raise ValueError(
                "WEEX private API credentials are required for authenticated account access"
            )

        query_string = urlencode(query or {})
        body_json = json.dumps(body, separators=(",", ":"), sort_keys=True) if body else ""
        timestamp = str(int(time.time() * 1000))
        payload = f"{timestamp}GET{path}"

        if body is not None:
            payload = f"{timestamp}POST{path}"
        if query_string:
            payload = f"{payload}?{query_string}"
        payload = f"{payload}{body_json}"

        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": self.api_passphrase,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
            "locale": self.locale,
        }

        url = f"{base_url.rstrip('/')}{path}"
        if query_string:
            url = f"{url}?{query_string}"

        return self.http_client.request_json(
            method="POST" if body is not None else "GET",
            url=url,
            headers=headers,
            body=body,
        )
