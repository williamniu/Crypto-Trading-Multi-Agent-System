from app.config.settings import Settings
from app.services.market_data_service import MarketDataService
from app.services.news_service import NewsService
from app.services.risk_service import RiskService


class StubWEEXClient:
    def get_contract_klines(self, *, symbol: str, interval: str, limit: int) -> list[list[object]]:
        assert symbol == "BTCUSDT"
        assert interval == "1h"
        assert limit == 3
        return [
            [1, "100", "101", "99", "100.5", "10", 2],
            [3, "100.5", "102", "100", "101.5", "12", 4],
            [5, "101.5", "103", "101", "102.5", "14", 6],
        ]

    def get_spot_klines(self, *, symbol: str, interval: str, limit: int) -> list[list[object]]:
        raise AssertionError("spot market client should not be used in this test")

    def get_contract_account_assets(self) -> list[dict[str, str]]:
        return [
            {
                "coinName": "USDT",
                "available": "5000",
                "frozen": "0",
                "equity": "5500",
                "unrealizePnl": "0",
            }
        ]

    def get_contract_positions(self, *, path: str) -> list[dict[str, str]]:
        assert path == "/capi/v3/position/allPosition"
        return [
            {"symbol": "BTCUSDT", "openValue": "1100"},
            {"symbol": "ETHUSDT", "openValue": "550"},
        ]


class StubTavilyClient:
    def search_news(
        self,
        *,
        query: str,
        max_results: int,
        search_depth: str,
        topic: str,
        days: int,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> dict[str, object]:
        assert "BTCUSDT" in query
        assert max_results == 4
        assert search_depth == "basic"
        assert topic == "news"
        assert days == 2
        assert include_domains == ["deepflow.tech", "mytoken.io"]
        assert exclude_domains == []
        return {
            "query": query,
            "results": [
                {
                    "title": "BTC ETF inflows jump again",
                    "url": "https://deepflow.tech/article-1",
                    "content": "ETF demand keeps climbing.",
                    "published_date": "2026-04-19",
                    "score": 0.9,
                },
                {
                    "title": "BTC ETF inflows jump again",
                    "url": "https://mytoken.io/article-duplicate",
                    "content": "duplicate title should be deduped",
                    "published_date": "2026-04-19",
                    "score": 0.7,
                },
                {
                    "title": "Macro tailwinds support BTC",
                    "url": "https://mytoken.io/article-2",
                    "content": "Macro backdrop improves.",
                    "published_date": "2026-04-19",
                    "score": 0.8,
                },
            ],
        }


def test_market_data_service_uses_weex_provider() -> None:
    settings = Settings(market_data_provider="weex")
    service = MarketDataService(settings=settings, weex_client=StubWEEXClient())

    candles = service.get_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=3)

    assert candles[0]["open"] == 100.0
    assert candles[-1]["close"] == 102.5
    assert candles[-1]["volume"] == 14.0


def test_news_service_uses_tavily_provider_and_domain_filters() -> None:
    settings = Settings(
        sentiment_provider="tavily",
        tavily_api_key="tvly-test",
        tavily_max_results=4,
        tavily_days=2,
        tavily_include_domains=["deepflow.tech", "mytoken.io"],
    )
    service = NewsService(settings=settings, tavily_client=StubTavilyClient())

    bundle = service.fetch_news_bundle(symbol="BTCUSDT")

    assert bundle["provider"] == "tavily"
    assert bundle["headlines"] == [
        "BTC ETF inflows jump again",
        "Macro tailwinds support BTC",
    ]
    assert len(bundle["items"]) == 2


def test_risk_service_uses_weex_account_snapshot() -> None:
    settings = Settings(
        risk_provider="weex",
        default_risk_per_trade=0.02,
        default_max_exposure=0.4,
        weex_positions_path="/capi/v3/position/allPosition",
    )
    service = RiskService(settings=settings, weex_client=StubWEEXClient())

    profile = service.normalize_profile(None)

    assert profile["account_balance"] == 5500.0
    assert profile["risk_per_trade"] == 0.02
    assert profile["max_exposure"] == 0.4
    assert round(profile["current_exposure"], 4) == round(1650 / 5500, 4)
