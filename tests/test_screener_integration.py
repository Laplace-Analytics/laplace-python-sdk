"""Integration tests for screener client."""

from unittest.mock import patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    PaginatedResponse,
    Region,
    ScreenerFilters,
    ScreenerLetterGrade,
    ScreenerRangeFilter,
    ScreenerSortBy,
    ScreenerStock,
    SortDirection,
)


class TestScreenerIntegration:
    """Integration tests for screener client with mocked API responses."""

    def test_screen_basic(self):
        mock_response_data = {
            "items": [
                {
                    "symbol": "AKBNK",
                    "price": 931.5,
                    "dailyChange": 27.12,
                    "marketCap": 4841200000000,
                    "peRatio": 84.6,
                    "pbRatio": 15.6,
                    "weeklyReturn": 0.417,
                    "monthlyReturn": 0.552,
                    "threeMonthReturn": 27.04,
                    "yearlyReturn": 27.47,
                    "threeYearReturn": 423.26,
                    "fiveYearReturn": 1589.99,
                    "ytdReturn": 27.04,
                    "compositeRating": 93,
                    "compositeScore": 88.2,
                    "rsRating": 88,
                    "rsScore": 0.91,
                    "perfQ1": 3.2,
                    "perfQ2": 5.1,
                    "perfQ3": 9.0,
                    "perfQ4": 12.4,
                    "epsRating": 85,
                    "epsScore": 0.77,
                    "epsGrowthYoy": 34.0,
                    "epsGrowthQoq": 21.0,
                    "epsTrailing4q": 65.2,
                    "epsAcceleration": True,
                    "adRating": "A",
                    "adScore": 0.65,
                    "upVolumeRatio": 1.4,
                    "volumeTrend": 0.2,
                    "smrRating": "B",
                    "smrScore": 0.72,
                    "salesGrowth2q": 18.0,
                    "grossMargin": 42.0,
                    "netMargin": 12.5,
                    "roe": 27.0,
                    "sma20": 305.1,
                    "sma50": 290.4,
                    "sma150": 250.7,
                    "sma200": 240.9,
                    "volumeSma50": 12500000,
                    "priceVsSma20": 2.4,
                    "priceVsSma50": 7.6,
                    "priceVsSma150": 24.6,
                    "priceVsSma200": 29.7,
                    "high52w": 320.0,
                    "low52w": 180.0,
                    "offHighPct": -2.3,
                    "volumeVsAvg50": 1.3,
                    "priceChangePct": 1.24,
                    "priceChangeAmount": 3.8,
                    "ytdChangePct": 12.4,
                }
            ],
            "recordCount": 511,
        }

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "_request", return_value=mock_response_data) as mock_request:
            response = client.screener.screen(
                region=Region.TR,
                filters=ScreenerFilters(
                    price=ScreenerRangeFilter(min=10.5, max=500.0),
                    pe_ratio=ScreenerRangeFilter(min=5.0),
                    composite_rating=ScreenerRangeFilter(min=90),
                    roe=ScreenerRangeFilter(min=20),
                    off_high_pct=ScreenerRangeFilter(min=-15, max=0),
                ),
                sort_by=ScreenerSortBy.COMPOSITE_RATING,
                sort_order=SortDirection.DESC,
                page=1,
                page_size=20,
            )

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "v1/screener"
        assert kwargs["params"] == {"region": "tr"}
        assert kwargs["json"] == {
            "page": 1,
            "pageSize": 20,
            "filters": {
                "price": {"min": 10.5, "max": 500.0},
                "peRatio": {"min": 5.0},
                "compositeRating": {"min": 90.0},
                "roe": {"min": 20.0},
                "offHighPct": {"min": -15.0, "max": 0.0},
            },
            "sortBy": "compositeRating",
            "sortOrder": "desc",
        }

        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 511
        assert len(response.items) == 1
        stock = response.items[0]
        assert isinstance(stock, ScreenerStock)
        assert stock.symbol == "AKBNK"
        assert stock.price == 931.5
        assert stock.daily_change == 27.12
        assert stock.market_cap == 4841200000000
        assert stock.pe_ratio == 84.6
        assert stock.pb_ratio == 15.6
        assert stock.weekly_return == 0.417
        assert stock.monthly_return == 0.552
        assert stock.three_month_return == 27.04
        assert stock.yearly_return == 27.47
        assert stock.three_year_return == 423.26
        assert stock.five_year_return == 1589.99
        assert stock.ytd_return == 27.04
        assert stock.composite_rating == 93
        assert stock.composite_score == 88.2
        assert stock.rs_rating == 88
        assert stock.rs_score == 0.91
        assert stock.eps_rating == 85
        assert stock.eps_acceleration is True
        assert stock.ad_rating == "A"
        assert stock.smr_rating == "B"
        assert stock.roe == 27.0
        assert stock.sma200 == 240.9
        assert stock.price_vs_sma200 == 29.7
        assert stock.off_high_pct == -2.3
        assert stock.ytd_change_pct == 12.4

    def test_screen_nullable_fields(self):
        mock_response_data = {
            "items": [{"symbol": "FOO", "price": None, "dailyChange": None}],
            "recordCount": 1,
        }

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "_request", return_value=mock_response_data):
            response = client.screener.screen(region=Region.TR)

        assert response.record_count == 1
        stock = response.items[0]
        assert stock.symbol == "FOO"
        assert stock.price is None
        assert stock.daily_change is None
        assert stock.market_cap is None

    def test_screen_no_filters_or_sort(self):
        mock_response_data = {"items": [], "recordCount": 0}
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "_request", return_value=mock_response_data) as mock_request:
            client.screener.screen(region=Region.TR, page=2, page_size=50)

        _, kwargs = mock_request.call_args
        assert kwargs["json"] == {"page": 2, "pageSize": 50}

    def test_screen_letter_grade_and_boolean_filters(self):
        mock_response_data = {"items": [], "recordCount": 0}
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "_request", return_value=mock_response_data) as mock_request:
            client.screener.screen(
                region=Region.TR,
                filters=ScreenerFilters(
                    smr_rating=[ScreenerLetterGrade.A, ScreenerLetterGrade.B],
                    ad_rating=[ScreenerLetterGrade.A],
                    eps_acceleration=True,
                ),
                sort_by=ScreenerSortBy.SMR_RATING,
            )

        _, kwargs = mock_request.call_args
        assert kwargs["json"] == {
            "page": 1,
            "pageSize": 20,
            "filters": {
                "smrRating": ["A", "B"],
                "adRating": ["A"],
                "epsAcceleration": True,
            },
            "sortBy": "smrRating",
        }

    def test_screen_eps_acceleration_false_is_sent(self):
        mock_response_data = {"items": [], "recordCount": 0}
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "_request", return_value=mock_response_data) as mock_request:
            client.screener.screen(
                region=Region.TR,
                filters=ScreenerFilters(eps_acceleration=False),
            )

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["filters"] == {"epsAcceleration": False}

    def test_screen_us_region_rejected(self):
        client = LaplaceClient(api_key="test-key")
        with pytest.raises(ValueError):
            client.screener.screen(region=Region.US)


class TestScreenerRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_screen(self, integration_client: LaplaceClient):
        response = integration_client.screener.screen(
            region=Region.TR,
            sort_by=ScreenerSortBy.MARKET_CAP,
            sort_order=SortDirection.DESC,
            page=1,
            page_size=10,
        )

        assert isinstance(response, PaginatedResponse)
        assert isinstance(response.record_count, int)
        assert response.record_count >= 0
        assert isinstance(response.items, list)
        if response.items:
            stock = response.items[0]
            assert isinstance(stock, ScreenerStock)
            assert stock.symbol
