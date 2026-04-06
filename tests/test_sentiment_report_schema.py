import pytest
from pydantic import ValidationError

from app.schemas.sentiment_report import SentimentReport


def test_sentiment_report_instantiation_success() -> None:
    report = SentimentReport(
        symbol="BTCUSDT",
        headline_count=2,
        sentiment_score=0.4,
        event_impact="positive",
        headlines=["ETF inflow rises", "Macro data supports risk assets"],
    )

    assert report.headline_count == 2
    assert isinstance(report.headlines, list)


def test_sentiment_report_default_headlines() -> None:
    report = SentimentReport(
        symbol="BTCUSDT",
        headline_count=0,
        sentiment_score=0.0,
        event_impact="neutral",
    )

    assert report.headlines == []


def test_sentiment_report_invalid_score_or_impact() -> None:
    with pytest.raises(ValidationError):
        SentimentReport(
            symbol="BTCUSDT",
            headline_count=1,
            sentiment_score=1.5,
            event_impact="positive",
            headlines=["dummy"],
        )

    with pytest.raises(ValidationError):
        SentimentReport(
            symbol="BTCUSDT",
            headline_count=1,
            sentiment_score=0.2,
            event_impact="mixed",
            headlines=["dummy"],
        )
