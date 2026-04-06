import pytest
from pydantic import ValidationError

from app.schemas.ta_report import TAIndicators, TALevels, TAReport


def test_ta_report_instantiation_success() -> None:
    report = TAReport(
        symbol="BTCUSDT",
        timeframe="1h",
        signal="bullish",
        confidence=0.72,
        indicators=TAIndicators(trend=2.1, momentum=0.3),
        levels=TALevels(support=100.0, resistance=110.0),
    )

    assert report.signal == "bullish"
    assert report.indicators.trend == 2.1


def test_ta_report_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        TAReport(
            symbol="BTCUSDT",
            timeframe="1h",
            signal="bullish",
            confidence=1.2,
            indicators={"trend": 1.0, "momentum": 0.1},
            levels={"support": 100.0, "resistance": 110.0},
        )


def test_ta_report_invalid_levels() -> None:
    with pytest.raises(ValidationError):
        TALevels(support=120.0, resistance=110.0)
