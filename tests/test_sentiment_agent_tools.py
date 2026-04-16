from app.agents.sentiment_analyst.agent import SentimentAnalystAgent
from app.agents.sentiment_analyst.toolset import SentimentAnalystToolset
from app.schemas.sentiment_report import SentimentReport


def test_sentiment_tool_registry_is_private_to_sentiment_agent() -> None:
    toolset = SentimentAnalystToolset()

    assert toolset.registry.list_tools() == [
        "classify_event",
        "fetch_news",
        "score_sentiment",
    ]


def test_sentiment_agent_generates_schema_valid_report() -> None:
    agent = SentimentAnalystAgent()

    report = agent.run({"symbol": "BTCUSDT"})
    validated = SentimentReport.model_validate(report)

    assert validated.headline_count == 3
    assert validated.event_impact == "positive"


def test_negative_sentiment_headlines_score_below_zero() -> None:
    toolset = SentimentAnalystToolset()

    scored = toolset.registry.execute(
        tool_name="score_sentiment",
        payload={
            "headlines": [
                "Exchange hack triggers liquidation fears",
                "Regulator lawsuit adds ban risk for token issuers",
            ]
        },
        agent_name="sentiment_analyst",
    )

    assert scored["score"] < 0
