from __future__ import annotations

from typing import Literal


BULLISH_TREND_THRESHOLD = 1.0
BEARISH_TREND_THRESHOLD = -1.0
BULLISH_MOMENTUM_THRESHOLD = 0.15
BEARISH_MOMENTUM_THRESHOLD = -0.15
BASE_CONFIDENCE = 0.55
NEUTRAL_CONFIDENCE_PENALTY = 0.10
MAX_CONFIDENCE = 0.95


def determine_signal(
    *,
    trend: float,
    momentum: float,
) -> Literal["bullish", "bearish", "neutral"]:
    """Convert raw TA metrics into an explicit directional signal."""

    if trend >= BULLISH_TREND_THRESHOLD and momentum >= BULLISH_MOMENTUM_THRESHOLD:
        return "bullish"
    if trend <= BEARISH_TREND_THRESHOLD and momentum <= BEARISH_MOMENTUM_THRESHOLD:
        return "bearish"
    return "neutral"


def determine_confidence(
    *,
    trend: float,
    momentum: float,
    signal: Literal["bullish", "bearish", "neutral"],
) -> float:
    """Map trend and momentum strength into a bounded confidence score."""

    trend_strength = min(abs(trend) / 6, 0.25)
    momentum_strength = min(abs(momentum) / 2, 0.15)
    confidence = BASE_CONFIDENCE + trend_strength + momentum_strength

    if signal == "neutral":
        confidence -= NEUTRAL_CONFIDENCE_PENALTY

    return round(max(0.50, min(MAX_CONFIDENCE, confidence)), 2)
