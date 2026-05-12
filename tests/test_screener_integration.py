"""Integration tests for screener client."""

from unittest.mock import patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    PaginatedResponse,
    Region,
    ScreenerFilters,
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
                ),
                sort_by=ScreenerSortBy.MARKET_CAP,
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
            },
            "sortBy": "marketCap",
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
