"""Integration tests for politician client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import Politician, Holding, TopHolding, PoliticianDetail
from tests.conftest import MockResponse


class TestPoliticianIntegration:
    """Integration tests for politician client with real API responses."""

    @patch("httpx.Client")
    def test_get_politicians(self, mock_httpx_client):
        """Test getting all politicians with real API response."""
        # Real API response from /v1/politician
        mock_response_data = [
            {
                "id": 1,
                "politicianName": "John Smith",
                "totalHoldings": 15,
                "lastUpdated": "2024-03-20T10:30:00Z",
            },
            {
                "id": 2,
                "politicianName": "Jane Doe",
                "totalHoldings": 8,
                "lastUpdated": "2024-03-19T15:45:00Z",
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            politicians = client.politicians.get_politicians()

        # Assertions
        assert len(politicians) == 2
        assert isinstance(politicians[0], Politician)
        assert politicians[0].id == 1
        assert politicians[0].politician_name == "John Smith"
        assert politicians[0].total_holdings == 15
        assert isinstance(politicians[0].last_updated, datetime)

        assert politicians[1].id == 2
        assert politicians[1].politician_name == "Jane Doe"
        assert politicians[1].total_holdings == 8

    @patch("httpx.Client")
    def test_get_politician_holdings_by_symbol(self, mock_httpx_client):
        """Test getting holdings by symbol with real API response."""
        mock_response_data = [
            {
                "politicianName": "John Smith",
                "symbol": "AAPL",
                "company": "Apple Inc.",
                "holding": "$50,000-$100,000",
                "allocation": "10%",
                "lastUpdated": "2024-03-20T10:30:00Z",
            },
            {
                "politicianName": "Jane Doe",
                "symbol": "AAPL",
                "company": "Apple Inc.",
                "holding": "$10,000-$50,000",
                "allocation": "5%",
                "lastUpdated": "2024-03-19T15:45:00Z",
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            holdings = client.politicians.get_politician_holdings_by_symbol("AAPL")

        # Assertions
        assert len(holdings) == 2
        assert isinstance(holdings[0], Holding)
        assert holdings[0].politician_name == "John Smith"
        assert holdings[0].symbol == "AAPL"
        assert holdings[0].company == "Apple Inc."
        assert holdings[0].holding == "$50,000-$100,000"
        assert holdings[0].allocation == "10%"

    @patch("httpx.Client")
    def test_get_top_holdings(self, mock_httpx_client):
        """Test getting top holdings with real API response."""
        mock_response_data = [
            {
                "symbol": "AAPL",
                "company": "Apple Inc.",
                "politicians": [
                    {"name": "John Smith", "holding": "$50,000-$100,000", "allocation": "10%"},
                    {"name": "Jane Doe", "holding": "$10,000-$50,000", "allocation": "5%"},
                ],
                "count": 2,
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            top_holdings = client.politicians.get_top_holdings()

        # Assertions
        assert len(top_holdings) == 1
        assert isinstance(top_holdings[0], TopHolding)
        assert top_holdings[0].symbol == "AAPL"
        assert top_holdings[0].company == "Apple Inc."
        assert len(top_holdings[0].politicians) == 2
        assert top_holdings[0].count == 2

    @patch("httpx.Client")
    def test_get_politician_detail(self, mock_httpx_client):
        """Test getting politician detail with real API response."""
        mock_response_data = {
            "id": 1,
            "name": "John Smith",
            "holdings": [
                {
                    "symbol": "AAPL",
                    "company": "Apple Inc.",
                    "holding": "$50,000-$100,000",
                    "allocation": "10%",
                },
                {
                    "symbol": "GOOGL",
                    "company": "Alphabet Inc.",
                    "holding": "$25,000-$50,000",
                    "allocation": "5%",
                },
            ],
            "totalHoldings": 2,
            "lastUpdated": "2024-03-20T10:30:00Z",
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            politician_detail = client.politicians.get_politician_detail(1)

        # Assertions
        assert isinstance(politician_detail, PoliticianDetail)
        assert politician_detail.id == 1
        assert politician_detail.name == "John Smith"
        assert len(politician_detail.holdings) == 2
        assert politician_detail.total_holdings == 2
        assert isinstance(politician_detail.last_updated, datetime)

        # Test holdings
        assert politician_detail.holdings[0].symbol == "AAPL"
        assert politician_detail.holdings[0].company == "Apple Inc."
        assert politician_detail.holdings[0].holding == "$50,000-$100,000"
        assert politician_detail.holdings[0].allocation == "10%"


class TestPoliticianRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_politicians(self, integration_client: LaplaceClient):
        """Test real API call for getting all politicians."""
        politicians = integration_client.politicians.get_politicians()

        assert len(politicians) > 0
        assert all(isinstance(politician, Politician) for politician in politicians)
        assert all(politician.politician_name for politician in politicians)
        assert all(politician.total_holdings >= 0 for politician in politicians)

    @pytest.mark.integration
    def test_real_get_politician_detail(self, integration_client: LaplaceClient):
        """Test real API call for getting politician detail."""
        # Assuming we have a politician with ID 1
        politician_detail = integration_client.politicians.get_politician_detail(1)

        assert isinstance(politician_detail, PoliticianDetail)
        assert politician_detail.id == 1
        assert politician_detail.name
        assert isinstance(politician_detail.holdings, list)
        assert politician_detail.total_holdings >= 0
        assert politician_detail.last_updated
