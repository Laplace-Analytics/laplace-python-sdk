"""Integration tests for halka arz (IPO) client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    HalkaArz,
    Region,
    PaginationPageSize,
    PaginatedResponse,
)
from tests.conftest import MockResponse


def _mock_ipo(**overrides):
    data = {
        "id": 1,
        "companyName": "Test Company A.Ş.",
        "symbol": "TEST",
        "instrumentId": None,
        "priceMin": 10.5,
        "priceMax": 10.5,
        "demandStartDate": "2024-03-01T00:00:00.000Z",
        "demandEndDate": "2024-03-03T00:00:00.000Z",
        "firstTradingDate": "2024-03-10T00:00:00.000Z",
        "sharesOffered": 1000000,
        "offeringSize": 10500000,
        "offeringType": "capital_increase",
        "consortiumLeader": "Test Yatırım",
        "additionalShares": None,
        "distributionMethod": None,
        "freeFloatRate": None,
        "intendedMarket": None,
        "sector": None,
        "maxLotPerInvestor": None,
        "currency": "TRY",
        "relatedDisclosureIds": [1001, 1002],
        "reviewed": False,
        "createdAt": "2024-02-20T00:00:00.000Z",
        "updatedAt": "2024-02-20T00:00:00.000Z",
        "status": "allocated",
        "isFixedPrice": True,
    }
    data.update(overrides)
    return data


class TestHalkaArzIntegration:
    """Integration tests for halka arz client with mocked API responses."""

    @patch("httpx.Client")
    def test_get_all(self, mock_httpx_client):
        """Test getting all IPO offerings."""
        mock_response_data = {"recordCount": 1, "items": [_mock_ipo()]}

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.halka_arz.get_all(
                region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
            )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 1
        assert len(response.items) == 1
        assert all(isinstance(item, HalkaArz) for item in response.items)

        ipo = response.items[0]
        assert ipo.id == 1
        assert ipo.company_name == "Test Company A.Ş."  # companyName -> company_name
        assert ipo.symbol == "TEST"
        assert ipo.instrument_id is None
        assert ipo.price_min == 10.5  # priceMin -> price_min
        assert ipo.price_max == 10.5
        assert isinstance(ipo.demand_start_date, datetime)  # demandStartDate -> demand_start_date
        assert ipo.offering_type == "capital_increase"
        assert ipo.consortium_leader == "Test Yatırım"
        assert ipo.currency == "TRY"
        assert ipo.related_disclosure_ids == [1001, 1002]
        assert ipo.reviewed is False
        assert ipo.status == "allocated"
        assert ipo.is_fixed_price is True  # isFixedPrice -> is_fixed_price

    @patch("httpx.Client")
    def test_get_by_id(self, mock_httpx_client):
        """Test getting a single IPO offering by id."""
        mock_response_data = _mock_ipo(id=42, symbol="ACME")

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.halka_arz.get_by_id(42)

        assert isinstance(response, HalkaArz)
        assert response.id == 42
        assert response.symbol == "ACME"
        assert response.company_name == "Test Company A.Ş."

    def test_get_all_rejects_non_tr_region(self):
        """The IPO endpoint only supports the 'tr' region."""
        client = LaplaceClient(api_key="test-key")

        with pytest.raises(ValueError):
            client.halka_arz.get_all(region=Region.US)


class TestHalkaArzRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_all(self, integration_client: LaplaceClient):
        """Test real API call for getting all IPO offerings."""
        response = integration_client.halka_arz.get_all(
            region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert all(isinstance(item, HalkaArz) for item in response.items)

        if response.items:
            assert all(item.id for item in response.items)
            assert all(item.company_name for item in response.items)
            assert all(item.status for item in response.items)
