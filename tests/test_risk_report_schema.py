import pytest
from pydantic import ValidationError

from app.schemas.risk_report import RiskReport


def test_risk_report_instantiation_success() -> None:
    report = RiskReport(
        position_size=500.0,
        risk_amount=100.0,
        total_exposure=0.2,
        exposure_ok=True,
        approved=True,
    )

    assert report.approved is True
    assert report.reasons == []


def test_risk_report_invalid_position_size() -> None:
    with pytest.raises(ValidationError):
        RiskReport(
            position_size=0,
            risk_amount=100.0,
            total_exposure=0.2,
            exposure_ok=True,
            approved=True,
        )


def test_risk_report_invalid_risk_amount() -> None:
    with pytest.raises(ValidationError):
        RiskReport(
            position_size=500.0,
            risk_amount=-1,
            total_exposure=0.2,
            exposure_ok=True,
            approved=True,
        )
