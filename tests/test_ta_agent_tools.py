import pytest

from app.agents.base.base_tool import ToolValidationError
from app.agents.ta_analyst.agent import TAAnalystAgent
from app.agents.ta_analyst.toolset import TAAnalystToolset
from app.schemas.ta_report import TAReport


def test_ta_tool_registry_is_private_to_ta_agent() -> None:
    toolset = TAAnalystToolset()

    assert toolset.registry.list_tools() == [
        "calc_indicator",
        "detect_levels",
        "get_ohlcv",
    ]


def test_ta_agent_generates_schema_valid_report() -> None:
    agent = TAAnalystAgent()

    report = agent.run({"symbol": "BTCUSDT", "timeframe": "1h"})
    validated = TAReport.model_validate(report)

    assert validated.signal == "bullish"
    assert validated.levels.support <= validated.levels.resistance


def test_ta_indicator_tool_rejects_short_candle_series() -> None:
    toolset = TAAnalystToolset()

    with pytest.raises(ValueError):
        toolset.registry.execute(
            tool_name="calc_indicator",
            payload={"candles": [{"close": 100.0}, {"close": 101.0}]},
            agent_name="ta_analyst",
        )


def test_ta_get_ohlcv_requires_symbol() -> None:
    toolset = TAAnalystToolset()

    with pytest.raises(ToolValidationError):
        toolset.registry.execute(
            tool_name="get_ohlcv",
            payload={"timeframe": "1h"},
            agent_name="ta_analyst",
        )
