from __future__ import annotations


MIN_RR_RATIO = 1.50


def approve_trade_plan(*, exposure_ok: bool, rr_ratio: float) -> dict[str, object]:
    """Apply explicit risk gates to the draft trade plan."""

    approved = True
    reasons: list[str] = []

    if not exposure_ok:
        approved = False
        reasons.append("Exposure exceeds max threshold")

    if rr_ratio < MIN_RR_RATIO:
        approved = False
        reasons.append("Risk/reward ratio below 1.5")

    if approved:
        reasons.append("Plan meets MVP risk rules")

    return {"approved": approved, "reasons": reasons}
