"""Integration tests for state client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    MarketState,
    Region,
    PaginationPageSize,
    PaginatedResponse,
)
from tests.conftest import MockResponse


class TestStateIntegration:
    """Integration tests for state client with real API responses."""

    @patch("httpx.Client")
    def test_get_all_market_states(self, mock_httpx_client):
        """Test getting all market states with real API response."""
        # Real API response from /api/v1/state/all?region=tr&page=0&size=10
        mock_response_data = {
            "recordCount": 3,
            "items": [
                {
                    "id": 526,
                    "marketSymbol": "BUYIN",
                    "state": "DISSEMINATION_OF_PRICE_LIMITS",
                    "lastTimestamp": "2025-08-01T20:33:00.162Z",
                },
                {
                    "id": 542,
                    "marketSymbol": "MSPOT",
                    "state": "DISSEMINATION_OF_PRICE_LIMITS",
                    "lastTimestamp": "2025-08-01T20:33:00.177Z",
                },
                {
                    "id": 3596,
                    "marketSymbol": "ODDLT",
                    "state": "BREAK",
                    "lastTimestamp": "2025-08-01T20:00:00.693Z",
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.state.get_all_market_states(
                region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 3
        assert len(response.items) == 3
        assert all(isinstance(item, MarketState) for item in response.items)

        # Test first market state (BUYIN)
        bist100 = response.items[0]
        assert bist100.id == 526
        assert bist100.market_symbol == "BUYIN"
        assert bist100.state == "DISSEMINATION_OF_PRICE_LIMITS"
        assert isinstance(bist100.last_timestamp, datetime)
        assert bist100.stock_symbol is None

        # Test second market state (MSPOT)
        bist30 = response.items[1]
        assert bist30.id == 542
        assert bist30.market_symbol == "MSPOT"
        assert bist30.state == "DISSEMINATION_OF_PRICE_LIMITS"
        assert isinstance(bist30.last_timestamp, datetime)
        assert bist30.stock_symbol is None

        # Test third market state (ODDLT)
        bist50 = response.items[2]
        assert bist50.id == 3596
        assert bist50.market_symbol == "ODDLT"
        assert bist50.state == "BREAK"
        assert isinstance(bist50.last_timestamp, datetime)
        assert bist50.stock_symbol is None

    @patch("httpx.Client")
    def test_get_market_state(self, mock_httpx_client):
        """Test getting market state by symbol with real API response."""
        # Real API response from /api/v1/state/BUYIN?region=tr
        mock_response_data = {
            "id": 526,
            "marketSymbol": "BUYIN",
            "state": "DISSEMINATION_OF_PRICE_LIMITS",
            "lastTimestamp": "2025-08-01T20:33:00.162Z",
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            market_state = client.state.get_market_state(symbol="BUYIN", region=Region.TR)

        # Assertions
        assert isinstance(market_state, MarketState)
        assert market_state.id == 526
        assert market_state.market_symbol == "BUYIN"
        assert market_state.state == "DISSEMINATION_OF_PRICE_LIMITS"
        assert isinstance(market_state.last_timestamp, datetime)
        assert market_state.stock_symbol is None

    @patch("httpx.Client")
    def test_get_all_stock_states(self, mock_httpx_client):
        """Test getting all stock states with real API response."""
        # Real API response from /api/v1/state/stock/all?region=tr&page=0&size=10
        mock_response_data = {
            "recordCount": 2,
            "items": [
                {
                    "id": 101,
                    "marketSymbol": None,
                    "state": "trading",
                    "lastTimestamp": "2024-01-15T10:30:00.000Z",
                    "stockSymbol": "AKBNK",
                },
                {
                    "id": 102,
                    "marketSymbol": None,
                    "state": "halted",
                    "lastTimestamp": "2024-01-15T10:30:00.000Z",
                    "stockSymbol": "GARAN",
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.state.get_all_stock_states(
                region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 2
        assert len(response.items) == 2
        assert all(isinstance(item, MarketState) for item in response.items)

        # Test first stock state (AKBNK)
        akbnk = response.items[0]
        assert akbnk.id == 101
        assert akbnk.market_symbol is None
        assert akbnk.state == "trading"
        assert isinstance(akbnk.last_timestamp, datetime)
        assert akbnk.stock_symbol == "AKBNK"

        # Test second stock state (GARAN)
        garan = response.items[1]
        assert garan.id == 102
        assert garan.market_symbol is None
        assert garan.state == "halted"
        assert isinstance(garan.last_timestamp, datetime)
        assert garan.stock_symbol == "GARAN"

    @patch("httpx.Client")
    def test_get_stock_state(self, mock_httpx_client):
        """Test getting stock state by symbol with real API response."""
        # Real API response from /api/v1/state/stock/AKBNK?region=tr
        mock_response_data = {
            "id": 101,
            "marketSymbol": None,
            "state": "trading",
            "lastTimestamp": "2024-01-15T10:30:00.000Z",
            "stockSymbol": "AKBNK",
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            stock_state = client.state.get_stock_state(symbol="AKBNK", region=Region.TR)

        # Assertions
        assert isinstance(stock_state, MarketState)
        assert stock_state.id == 101
        assert stock_state.market_symbol is None
        assert stock_state.state == "trading"
        assert isinstance(stock_state.last_timestamp, datetime)
        assert stock_state.stock_symbol == "AKBNK"

    @patch("httpx.Client")
    def test_state_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for state data."""
        mock_response_data = {
            "id": 1,
            "marketSymbol": "TEST",
            "state": "open",
            "lastTimestamp": "2024-01-01T00:00:00.000Z",
            "stockSymbol": "TESTSTOCK",
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            state = client.state.get_market_state(symbol="TEST", region=Region.TR)

        # Test field aliases work
        assert state.market_symbol == "TEST"  # marketSymbol -> market_symbol
        assert isinstance(state.last_timestamp, datetime)  # lastTimestamp -> last_timestamp
        assert state.stock_symbol == "TESTSTOCK"  # stockSymbol -> stock_symbol


class TestStateRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_all_market_states(self, integration_client: LaplaceClient):
        """Test real API call for getting all market states."""
        response = integration_client.state.get_all_market_states(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(item, MarketState) for item in response.items)

        # Test items if any exist
        if response.items:
            assert all(item.id for item in response.items)
            assert all(item.state for item in response.items)
            assert all(isinstance(item.last_timestamp, datetime) for item in response.items)
            # market_symbol and stock_symbol can be None

    @pytest.mark.integration
    def test_real_get_market_state(self, integration_client: LaplaceClient):
        """Test real API call for getting market state by symbol."""
        # Use a known market symbol for testing
        symbol = "BUYIN"

        market_state = integration_client.state.get_market_state(symbol=symbol, region=Region.TR)

        assert isinstance(market_state, MarketState)
        assert market_state.id
        assert market_state.state
        assert isinstance(market_state.last_timestamp, datetime)
        # market_symbol and stock_symbol can be None

    @pytest.mark.integration
    def test_real_get_all_stock_states(self, integration_client: LaplaceClient):
        """Test real API call for getting all stock states."""
        response = integration_client.state.get_all_stock_states(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(item, MarketState) for item in response.items)

        # Test items if any exist
        if response.items:
            assert all(item.id for item in response.items)
            assert all(item.state for item in response.items)
            assert all(isinstance(item.last_timestamp, datetime) for item in response.items)
            # market_symbol and stock_symbol can be None

    @pytest.mark.integration
    def test_real_get_stock_state(self, integration_client: LaplaceClient):
        """Test real API call for getting stock state by symbol."""
        # Use a known stock symbol for testing
        symbol = "AKBNK"

        stock_state = integration_client.state.get_stock_state(symbol=symbol, region=Region.TR)

        assert isinstance(stock_state, MarketState)
        assert stock_state.id
        assert stock_state.state
        assert isinstance(stock_state.last_timestamp, datetime)
        # market_symbol and stock_symbol can be None
