"""Integration tests for capital increase client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    CapitalIncrease,
    CapitalIncreaseType,
    Region,
    PaginationPageSize,
    PaginatedResponse,
)
from tests.conftest import MockResponse


class TestCapitalIncreaseIntegration:
    """Integration tests for capital increase client with real API responses."""

    @patch("httpx.Client")
    def test_get_all_capital_increases(self, mock_httpx_client):
        """Test getting all capital increases with real API response."""
        # Real API response from /api/v1/capital-increase/all?region=tr&page=0&size=10
        mock_response_data = {
            "recordCount": 3,
            "items": [
                {
                    "id": 1,
                    "types": ["rights", "bonus"],
                    "symbol": "AKBNK",
                    "bonusRate": "50%",
                    "rightsRate": "25%",
                    "paymentDate": "2024-03-15T00:00:00.000Z",
                    "rightsPrice": "15.50",
                    "rightsEndDate": "2024-04-15T00:00:00.000Z",
                    "targetCapital": "1000000000",
                    "bonusStartDate": "2024-03-01T00:00:00.000Z",
                    "currentCapital": "800000000",
                    "rightsStartDate": "2024-03-10T00:00:00.000Z",
                    "spkApprovalDate": "2024-02-15",
                    "bonusTotalAmount": "400000000",
                    "registrationDate": "2024-02-20T00:00:00.000Z",
                    "boardDecisionDate": "2024-01-15T00:00:00.000Z",
                    "bonusDividendRate": "10%",
                    "rightsTotalAmount": "200000000",
                    "specifiedCurrency": "TRY",
                    "rightsLastSellDate": "2024-04-10T00:00:00.000Z",
                    "spkApplicationDate": "2024-01-20T00:00:00.000Z",
                    "relatedDisclosureIds": [12345, 12346],
                    "spkApplicationResult": "Approved",
                    "bonusDividendTotalAmount": "80000000",
                    "registeredCapitalCeiling": "1200000000",
                    "externalCapitalIncreaseRate": "5%",
                    "externalCapitalIncreaseAmount": "100000000",
                },
                {
                    "id": 2,
                    "types": ["bonus"],
                    "symbol": "GARAN",
                    "bonusRate": "30%",
                    "rightsRate": None,
                    "paymentDate": "2024-04-01T00:00:00.000Z",
                    "rightsPrice": None,
                    "rightsEndDate": None,
                    "targetCapital": "800000000",
                    "bonusStartDate": "2024-03-15T00:00:00.000Z",
                    "currentCapital": "600000000",
                    "rightsStartDate": None,
                    "spkApprovalDate": "2024-02-20",
                    "bonusTotalAmount": "240000000",
                    "registrationDate": "2024-03-01T00:00:00.000Z",
                    "boardDecisionDate": "2024-01-20T00:00:00.000Z",
                    "bonusDividendRate": "5%",
                    "rightsTotalAmount": None,
                    "specifiedCurrency": "TRY",
                    "rightsLastSellDate": None,
                    "spkApplicationDate": "2024-01-25T00:00:00.000Z",
                    "relatedDisclosureIds": [23456],
                    "spkApplicationResult": "Approved",
                    "bonusDividendTotalAmount": "30000000",
                    "registeredCapitalCeiling": "900000000",
                    "externalCapitalIncreaseRate": None,
                    "externalCapitalIncreaseAmount": None,
                },
                {
                    "id": 3,
                    "types": ["external"],
                    "symbol": "ISBANK",
                    "bonusRate": None,
                    "rightsRate": None,
                    "paymentDate": "2024-05-01T00:00:00.000Z",
                    "rightsPrice": None,
                    "rightsEndDate": None,
                    "targetCapital": "1200000000",
                    "bonusStartDate": None,
                    "currentCapital": "1000000000",
                    "rightsStartDate": None,
                    "spkApprovalDate": "2024-03-15",
                    "bonusTotalAmount": None,
                    "registrationDate": "2024-04-01T00:00:00.000Z",
                    "boardDecisionDate": "2024-02-01T00:00:00.000Z",
                    "bonusDividendRate": None,
                    "rightsTotalAmount": None,
                    "specifiedCurrency": "TRY",
                    "rightsLastSellDate": None,
                    "spkApplicationDate": "2024-02-05T00:00:00.000Z",
                    "relatedDisclosureIds": [34567, 34568, 34569],
                    "spkApplicationResult": "Pending",
                    "bonusDividendTotalAmount": None,
                    "registeredCapitalCeiling": "1400000000",
                    "externalCapitalIncreaseRate": "20%",
                    "externalCapitalIncreaseAmount": "200000000",
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.capital_increase.get_all(
                region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 3
        assert len(response.items) == 3
        assert all(isinstance(item, CapitalIncrease) for item in response.items)

        # Test first capital increase (AKBNK)
        akbnk = response.items[0]
        assert akbnk.id == 1
        assert akbnk.symbol == "AKBNK"
        assert akbnk.types == [CapitalIncreaseType.RIGHTS, CapitalIncreaseType.BONUS]
        assert akbnk.bonus_rate == "50%"
        assert akbnk.rights_rate == "25%"
        assert isinstance(akbnk.payment_date, datetime)
        assert akbnk.rights_price == "15.50"
        assert isinstance(akbnk.rights_end_date, datetime)
        assert akbnk.target_capital == "1000000000"
        assert isinstance(akbnk.bonus_start_date, datetime)
        assert akbnk.current_capital == "800000000"
        assert isinstance(akbnk.rights_start_date, datetime)
        assert akbnk.spk_approval_date == "2024-02-15"
        assert akbnk.bonus_total_amount == "400000000"
        assert isinstance(akbnk.registration_date, datetime)
        assert isinstance(akbnk.board_decision_date, datetime)
        assert akbnk.bonus_dividend_rate == "10%"
        assert akbnk.rights_total_amount == "200000000"
        assert akbnk.specified_currency == "TRY"
        assert isinstance(akbnk.rights_last_sell_date, datetime)
        assert isinstance(akbnk.spk_application_date, datetime)
        assert akbnk.related_disclosure_ids == [12345, 12346]
        assert akbnk.spk_application_result == "Approved"
        assert akbnk.bonus_dividend_total_amount == "80000000"
        assert akbnk.registered_capital_ceiling == "1200000000"
        assert akbnk.external_capital_increase_rate == "5%"
        assert akbnk.external_capital_increase_amount == "100000000"

        # Test second capital increase (GARAN)
        garan = response.items[1]
        assert garan.id == 2
        assert garan.symbol == "GARAN"
        assert garan.types == [CapitalIncreaseType.BONUS]
        assert garan.bonus_rate == "30%"
        assert garan.rights_rate is None
        assert isinstance(garan.payment_date, datetime)
        assert garan.rights_price is None
        assert garan.rights_end_date is None
        assert garan.target_capital == "800000000"
        assert isinstance(garan.bonus_start_date, datetime)
        assert garan.current_capital == "600000000"
        assert garan.rights_start_date is None
        assert garan.spk_approval_date == "2024-02-20"
        assert garan.bonus_total_amount == "240000000"
        assert isinstance(garan.registration_date, datetime)
        assert isinstance(garan.board_decision_date, datetime)
        assert garan.bonus_dividend_rate == "5%"
        assert garan.rights_total_amount is None
        assert garan.specified_currency == "TRY"
        assert garan.rights_last_sell_date is None
        assert isinstance(garan.spk_application_date, datetime)
        assert garan.related_disclosure_ids == [23456]
        assert garan.spk_application_result == "Approved"
        assert garan.bonus_dividend_total_amount == "30000000"
        assert garan.registered_capital_ceiling == "900000000"
        assert garan.external_capital_increase_rate is None
        assert garan.external_capital_increase_amount is None

        # Test third capital increase (ISBANK)
        isbank = response.items[2]
        assert isbank.id == 3
        assert isbank.symbol == "ISBANK"
        assert isbank.types == [CapitalIncreaseType.EXTERNAL]
        assert isbank.bonus_rate is None
        assert isbank.rights_rate is None
        assert isinstance(isbank.payment_date, datetime)
        assert isbank.rights_price is None
        assert isbank.rights_end_date is None
        assert isbank.target_capital == "1200000000"
        assert isbank.bonus_start_date is None
        assert isbank.current_capital == "1000000000"
        assert isbank.rights_start_date is None
        assert isbank.spk_approval_date == "2024-03-15"
        assert isbank.bonus_total_amount is None
        assert isinstance(isbank.registration_date, datetime)
        assert isinstance(isbank.board_decision_date, datetime)
        assert isbank.bonus_dividend_rate is None
        assert isbank.rights_total_amount is None
        assert isbank.specified_currency == "TRY"
        assert isbank.rights_last_sell_date is None
        assert isinstance(isbank.spk_application_date, datetime)
        assert isbank.related_disclosure_ids == [34567, 34568, 34569]
        assert isbank.spk_application_result == "Pending"
        assert isbank.bonus_dividend_total_amount is None
        assert isbank.registered_capital_ceiling == "1400000000"
        assert isbank.external_capital_increase_rate == "20%"
        assert isbank.external_capital_increase_amount == "200000000"

    @patch("httpx.Client")
    def test_get_capital_increase_by_symbol(self, mock_httpx_client):
        """Test getting capital increase by symbol with real API response."""
        # Real API response from /api/v1/capital-increase/AKBNK?region=tr&page=0&size=10
        mock_response_data = {
            "recordCount": 1,
            "items": [
                {
                    "id": 1,
                    "types": ["rights", "bonus"],
                    "symbol": "AKBNK",
                    "bonusRate": "50%",
                    "rightsRate": "25%",
                    "paymentDate": "2024-03-15T00:00:00.000Z",
                    "rightsPrice": "15.50",
                    "rightsEndDate": "2024-04-15T00:00:00.000Z",
                    "targetCapital": "1000000000",
                    "bonusStartDate": "2024-03-01T00:00:00.000Z",
                    "currentCapital": "800000000",
                    "rightsStartDate": "2024-03-10T00:00:00.000Z",
                    "spkApprovalDate": "2024-02-15",
                    "bonusTotalAmount": "400000000",
                    "registrationDate": "2024-02-20T00:00:00.000Z",
                    "boardDecisionDate": "2024-01-15T00:00:00.000Z",
                    "bonusDividendRate": "10%",
                    "rightsTotalAmount": "200000000",
                    "specifiedCurrency": "TRY",
                    "rightsLastSellDate": "2024-04-10T00:00:00.000Z",
                    "spkApplicationDate": "2024-01-20T00:00:00.000Z",
                    "relatedDisclosureIds": [12345, 12346],
                    "spkApplicationResult": "Approved",
                    "bonusDividendTotalAmount": "80000000",
                    "registeredCapitalCeiling": "1200000000",
                    "externalCapitalIncreaseRate": "5%",
                    "externalCapitalIncreaseAmount": "100000000",
                }
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.capital_increase.get_by_symbol(
                symbol="AKBNK", region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 1
        assert len(response.items) == 1
        assert all(isinstance(item, CapitalIncrease) for item in response.items)

        # Test capital increase
        capital_increase = response.items[0]
        assert capital_increase.id == 1
        assert capital_increase.symbol == "AKBNK"
        assert capital_increase.types == [CapitalIncreaseType.RIGHTS, CapitalIncreaseType.BONUS]
        assert capital_increase.bonus_rate == "50%"
        assert capital_increase.rights_rate == "25%"
        assert isinstance(capital_increase.payment_date, datetime)
        assert capital_increase.rights_price == "15.50"
        assert isinstance(capital_increase.rights_end_date, datetime)
        assert capital_increase.target_capital == "1000000000"
        assert isinstance(capital_increase.bonus_start_date, datetime)
        assert capital_increase.current_capital == "800000000"
        assert isinstance(capital_increase.rights_start_date, datetime)
        assert capital_increase.spk_approval_date == "2024-02-15"
        assert capital_increase.bonus_total_amount == "400000000"
        assert isinstance(capital_increase.registration_date, datetime)
        assert isinstance(capital_increase.board_decision_date, datetime)
        assert capital_increase.bonus_dividend_rate == "10%"
        assert capital_increase.rights_total_amount == "200000000"
        assert capital_increase.specified_currency == "TRY"
        assert isinstance(capital_increase.rights_last_sell_date, datetime)
        assert isinstance(capital_increase.spk_application_date, datetime)
        assert capital_increase.related_disclosure_ids == [12345, 12346]
        assert capital_increase.spk_application_result == "Approved"
        assert capital_increase.bonus_dividend_total_amount == "80000000"
        assert capital_increase.registered_capital_ceiling == "1200000000"
        assert capital_increase.external_capital_increase_rate == "5%"
        assert capital_increase.external_capital_increase_amount == "100000000"

    @patch("httpx.Client")
    def test_get_active_rights(self, mock_httpx_client):
        """Test getting active rights with real API response."""
        # Real API response from /api/v1/rights/active/AKBNK?region=tr
        mock_response_data = [
            {
                "id": 1,
                "types": ["rights"],
                "symbol": "AKBNK",
                "bonusRate": None,
                "rightsRate": "25%",
                "paymentDate": "2024-03-15T00:00:00.000Z",
                "rightsPrice": "15.50",
                "rightsEndDate": "2024-04-15T00:00:00.000Z",
                "targetCapital": "1000000000",
                "bonusStartDate": None,
                "currentCapital": "800000000",
                "rightsStartDate": "2024-03-10T00:00:00.000Z",
                "spkApprovalDate": "2024-02-15",
                "bonusTotalAmount": None,
                "registrationDate": "2024-02-20T00:00:00.000Z",
                "boardDecisionDate": "2024-01-15T00:00:00.000Z",
                "bonusDividendRate": None,
                "rightsTotalAmount": "200000000",
                "specifiedCurrency": "TRY",
                "rightsLastSellDate": "2024-04-10T00:00:00.000Z",
                "spkApplicationDate": "2024-01-20T00:00:00.000Z",
                "relatedDisclosureIds": [12345, 12346],
                "spkApplicationResult": "Approved",
                "bonusDividendTotalAmount": None,
                "registeredCapitalCeiling": "1200000000",
                "externalCapitalIncreaseRate": None,
                "externalCapitalIncreaseAmount": None,
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.capital_increase.get_active_rights(symbol="AKBNK", region=Region.TR)

        # Assertions
        assert isinstance(response, list)
        assert len(response) == 1
        assert all(isinstance(item, CapitalIncrease) for item in response)

        # Test active rights
        active_rights = response[0]
        assert active_rights.id == 1
        assert active_rights.symbol == "AKBNK"
        assert active_rights.types == [CapitalIncreaseType.RIGHTS]
        assert active_rights.bonus_rate is None
        assert active_rights.rights_rate == "25%"
        assert isinstance(active_rights.payment_date, datetime)
        assert active_rights.rights_price == "15.50"
        assert isinstance(active_rights.rights_end_date, datetime)
        assert active_rights.target_capital == "1000000000"
        assert active_rights.bonus_start_date is None
        assert active_rights.current_capital == "800000000"
        assert isinstance(active_rights.rights_start_date, datetime)
        assert active_rights.spk_approval_date == "2024-02-15"
        assert active_rights.bonus_total_amount is None
        assert isinstance(active_rights.registration_date, datetime)
        assert isinstance(active_rights.board_decision_date, datetime)
        assert active_rights.bonus_dividend_rate is None
        assert active_rights.rights_total_amount == "200000000"
        assert active_rights.specified_currency == "TRY"
        assert isinstance(active_rights.rights_last_sell_date, datetime)
        assert isinstance(active_rights.spk_application_date, datetime)
        assert active_rights.related_disclosure_ids == [12345, 12346]
        assert active_rights.spk_application_result == "Approved"
        assert active_rights.bonus_dividend_total_amount is None
        assert active_rights.registered_capital_ceiling == "1200000000"
        assert active_rights.external_capital_increase_rate is None
        assert active_rights.external_capital_increase_amount is None

    @patch("httpx.Client")
    def test_capital_increase_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for capital increase."""
        mock_response_data = {
            "recordCount": 1,
            "items": [
                {
                    "id": 1,
                    "types": ["rights"],
                    "symbol": "TEST",
                    "bonusRate": "30%",
                    "rightsRate": "20%",
                    "paymentDate": "2024-01-01T00:00:00.000Z",
                    "rightsPrice": "10.00",
                    "rightsEndDate": "2024-02-01T00:00:00.000Z",
                    "targetCapital": "500000000",
                    "bonusStartDate": "2024-01-15T00:00:00.000Z",
                    "currentCapital": "400000000",
                    "rightsStartDate": "2024-01-10T00:00:00.000Z",
                    "spkApprovalDate": "2023-12-15",
                    "bonusTotalAmount": "150000000",
                    "registrationDate": "2023-12-20T00:00:00.000Z",
                    "boardDecisionDate": "2023-11-15T00:00:00.000Z",
                    "bonusDividendRate": "5%",
                    "rightsTotalAmount": "100000000",
                    "specifiedCurrency": "TRY",
                    "rightsLastSellDate": "2024-01-25T00:00:00.000Z",
                    "spkApplicationDate": "2023-11-20T00:00:00.000Z",
                    "relatedDisclosureIds": [12345],
                    "spkApplicationResult": "Approved",
                    "bonusDividendTotalAmount": "20000000",
                    "registeredCapitalCeiling": "600000000",
                    "externalCapitalIncreaseRate": "10%",
                    "externalCapitalIncreaseAmount": "50000000",
                }
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.capital_increase.get_all(region=Region.TR)

        capital_increase = response.items[0]

        # Test field aliases work
        assert capital_increase.bonus_rate == "30%"  # bonusRate -> bonus_rate
        assert capital_increase.rights_rate == "20%"  # rightsRate -> rights_rate
        assert isinstance(capital_increase.payment_date, datetime)  # paymentDate -> payment_date
        assert capital_increase.rights_price == "10.00"  # rightsPrice -> rights_price
        assert isinstance(
            capital_increase.rights_end_date, datetime
        )  # rightsEndDate -> rights_end_date
        assert capital_increase.target_capital == "500000000"  # targetCapital -> target_capital
        assert isinstance(
            capital_increase.bonus_start_date, datetime
        )  # bonusStartDate -> bonus_start_date
        assert capital_increase.current_capital == "400000000"  # currentCapital -> current_capital
        assert isinstance(
            capital_increase.rights_start_date, datetime
        )  # rightsStartDate -> rights_start_date
        assert (
            capital_increase.spk_approval_date == "2023-12-15"
        )  # spkApprovalDate -> spk_approval_date
        assert (
            capital_increase.bonus_total_amount == "150000000"
        )  # bonusTotalAmount -> bonus_total_amount
        assert isinstance(
            capital_increase.registration_date, datetime
        )  # registrationDate -> registration_date
        assert isinstance(
            capital_increase.board_decision_date, datetime
        )  # boardDecisionDate -> board_decision_date
        assert (
            capital_increase.bonus_dividend_rate == "5%"
        )  # bonusDividendRate -> bonus_dividend_rate
        assert (
            capital_increase.rights_total_amount == "100000000"
        )  # rightsTotalAmount -> rights_total_amount
        assert (
            capital_increase.specified_currency == "TRY"
        )  # specifiedCurrency -> specified_currency
        assert isinstance(
            capital_increase.rights_last_sell_date, datetime
        )  # rightsLastSellDate -> rights_last_sell_date
        assert isinstance(
            capital_increase.spk_application_date, datetime
        )  # spkApplicationDate -> spk_application_date
        assert capital_increase.related_disclosure_ids == [
            12345
        ]  # relatedDisclosureIds -> related_disclosure_ids
        assert (
            capital_increase.spk_application_result == "Approved"
        )  # spkApplicationResult -> spk_application_result
        assert (
            capital_increase.bonus_dividend_total_amount == "20000000"
        )  # bonusDividendTotalAmount -> bonus_dividend_total_amount
        assert (
            capital_increase.registered_capital_ceiling == "600000000"
        )  # registeredCapitalCeiling -> registered_capital_ceiling
        assert (
            capital_increase.external_capital_increase_rate == "10%"
        )  # externalCapitalIncreaseRate -> external_capital_increase_rate
        assert (
            capital_increase.external_capital_increase_amount == "50000000"
        )  # externalCapitalIncreaseAmount -> external_capital_increase_amount


class TestCapitalIncreaseRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_all_capital_increases(self, integration_client: LaplaceClient):
        """Test real API call for getting all capital increases."""
        response = integration_client.capital_increase.get_all(
            region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(item, CapitalIncrease) for item in response.items)

        # Test items if any exist
        if response.items:
            assert all(item.id for item in response.items)
            assert all(item.symbol for item in response.items)
            assert all(item.types for item in response.items)
            assert all(isinstance(item.types, list) for item in response.items)
            assert all(
                all(isinstance(t, CapitalIncreaseType) for t in item.types)
                for item in response.items
            )

    @pytest.mark.integration
    def test_real_get_capital_increase_by_symbol(self, integration_client: LaplaceClient):
        """Test real API call for getting capital increase by symbol."""
        # Use a known stock symbol for testing
        symbol = "AKBNK"

        response = integration_client.capital_increase.get_by_symbol(
            symbol=symbol, region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(item, CapitalIncrease) for item in response.items)

        # Test items if any exist
        if response.items:
            assert all(item.id for item in response.items)
            # API may return symbol with .E suffix, so check if symbol starts with the requested symbol
            assert all(item.symbol.startswith(symbol) for item in response.items)
            assert all(item.types for item in response.items)
            assert all(isinstance(item.types, list) for item in response.items)
            assert all(
                all(isinstance(t, CapitalIncreaseType) for t in item.types)
                for item in response.items
            )

    @pytest.mark.integration
    def test_real_get_active_rights(self, integration_client: LaplaceClient):
        """Test real API call for getting active rights."""
        # Use a known stock symbol for testing
        symbol = "AKBNK"

        response = integration_client.capital_increase.get_active_rights(
            symbol=symbol, region=Region.TR
        )
        if len(response) == 0:
            return

        # get_active_rights returns a list, not PaginatedResponse
        assert isinstance(response, list)
        assert len(response) >= 0
        assert all(isinstance(item, CapitalIncrease) for item in response)

        # Test items if any exist
        if response:
            assert all(item.id for item in response)
            # API may return symbol with .E suffix, so check if symbol starts with the requested symbol
            assert all(item.symbol.startswith(symbol) for item in response)
            assert all(item.types for item in response)
            assert all(isinstance(item.types, list) for item in response)
            assert all(
                all(isinstance(t, CapitalIncreaseType) for t in item.types) for item in response
            )
