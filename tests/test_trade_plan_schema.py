import pytest
from pydantic import ValidationError

from app.schemas.trade_plan import TradePlan


def test_trade_plan_instantiation_success() -> None:
    plan = TradePlan(
        symbol="BTCUSDT",
        action="BUY",
        confidence=0.8,
        combined_score=0.5,
        stop_loss_pct=0.01,
        take_profit_pct=0.02,
        rr_ratio=2.0,
        target_exposure=0.05,
        position_size=1000,
        risk_amount=100,
        approved=True,
        ta_signal="bullish",
        sentiment_score=0.4,
    )

    assert plan.entry_hint == "market"
    assert plan.reasons == []
    assert plan.notes == []


def test_trade_plan_invalid_rr_window() -> None:
    with pytest.raises(ValidationError):
        TradePlan(
            symbol="BTCUSDT",
            action="BUY",
            confidence=0.8,
            combined_score=0.5,
            stop_loss_pct=0.02,
            take_profit_pct=0.01,
            rr_ratio=0.5,
            target_exposure=0.05,
            position_size=1000,
            risk_amount=100,
            approved=True,
            ta_signal="bullish",
            sentiment_score=0.4,
        )


def test_trade_plan_unapproved_must_hold() -> None:
    with pytest.raises(ValidationError):
        TradePlan(
            symbol="BTCUSDT",
            action="BUY",
            confidence=0.8,
            combined_score=0.5,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            rr_ratio=2.0,
            target_exposure=0.05,
            position_size=1000,
            risk_amount=100,
            approved=False,
            ta_signal="bullish",
            sentiment_score=0.4,
        )
