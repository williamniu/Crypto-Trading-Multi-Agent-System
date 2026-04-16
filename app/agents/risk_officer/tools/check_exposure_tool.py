from __future__ import annotations

from typing import Any

from app.agents.base.base_tool import BaseTool


class CheckExposureTool(BaseTool):
    """Ensure the new trade does not breach exposure limits."""

    def __init__(self) -> None:
        super().__init__(
            name="check_exposure",
            description="Check whether total exposure stays within max exposure.",
            required_fields=["current_exposure", "new_exposure", "max_exposure"],
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        current_exposure = float(payload["current_exposure"])
        new_exposure = float(payload["new_exposure"])
        max_exposure = float(payload["max_exposure"])
        total_exposure = current_exposure + new_exposure
        return {
            "total_exposure": round(total_exposure, 4),
            "exposure_ok": total_exposure <= max_exposure,
        }
