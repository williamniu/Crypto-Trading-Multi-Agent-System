from __future__ import annotations

from typing import Literal


POSITIVE_IMPACT_THRESHOLD = 0.40
NEGATIVE_IMPACT_THRESHOLD = -0.40


def classify_event_impact(score: float) -> Literal["positive", "negative", "neutral"]:
    """Translate normalized sentiment score into a constrained impact label."""

    if score >= POSITIVE_IMPACT_THRESHOLD:
        return "positive"
    if score <= NEGATIVE_IMPACT_THRESHOLD:
        return "negative"
    return "neutral"
