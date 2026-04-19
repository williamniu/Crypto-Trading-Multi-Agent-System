from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ExternalAPIError(RuntimeError):
    """Raised when an external provider request fails."""


@dataclass(frozen=True)
class HTTPJSONClient:
    """Small stdlib JSON HTTP client used by external provider adapters."""

    timeout_seconds: float = 10.0

    def request_json(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        payload: bytes | None = None
        request_headers = dict(headers or {})

        if body is not None:
            payload = json.dumps(body, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
            request_headers.setdefault("Content-Type", "application/json")

        request = Request(
            url=url,
            data=payload,
            headers=request_headers,
            method=method.upper(),
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ExternalAPIError(
                f"{method.upper()} {url} failed with HTTP {error.code}: {detail}"
            ) from error
        except URLError as error:
            raise ExternalAPIError(f"{method.upper()} {url} failed: {error.reason}") from error

        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise ExternalAPIError(
                f"{method.upper()} {url} returned invalid JSON: {raw[:200]}"
            ) from error
