"""Integration tests for financials client."""

from unittest.mock import Mock, patch

from laplace import LaplaceClient
from laplace.models import (
    Currency,
    FinancialSheetDate,
    FinancialSheetPeriod,
    FinancialSheetType,
    HistoricalFinancialSheets,
    HistoricalRatiosFormat,
    RatioComparisonPeerType,
    Region,
    StockHistoricalRatios,
    StockHistoricalRatiosDescription,
    StockPeerFinancialRatioComparison,
)
from tests.conftest import MockResponse


class TestFinancialsIntegration:
    """Integration tests for financials client with real API responses."""

    @patch("httpx.Client")
    def test_get_financial_ratio_comparison(self, mock_httpx_client):
        mock_response_data = [
            {
                "metricName": "pricing",
                "normalizedValue": 55.83839655089121,
                "data": [
                    {"slug": "F/K", "value": 39.982351568046845, "average": -37.57057174279183},
                ],
            },
        ]
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            result = client.financials.get_financial_ratio_comparison(
                symbol="TUPRS",
                region=Region.TR,
                peer_type=RatioComparisonPeerType.INDUSTRY,
            )
        assert isinstance(result, list)
        assert isinstance(result[0], StockPeerFinancialRatioComparison)
        assert result[0].metric_name == "pricing"
        assert result[0].normalized_value == 55.83839655089121
        assert isinstance(result[0].data, list)
        assert result[0].data[0].slug == "F/K"
        assert result[0].data[0].value == 39.982351568046845
        assert result[0].data[0].average == -37.57057174279183

    @patch("httpx.Client")
    def test_get_historical_ratios(self, mock_httpx_client):
        mock_response_data = [
            {
                "slug": "pe",
                "finalValue": 10.0,
                "threeYearGrowth": 0.15,
                "yearGrowth": 0.05,
                "finalSectorValue": 11.0,
                "currency": "TRY",
                "format": "decimal",
                "name": "Price/Earnings",
                "items": [{"period": "2023Q1", "value": 10.0, "sectorMean": 11.0}],
            }
        ]
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            result = client.financials.get_historical_ratios(
                symbol="TUPRS",
                keys=["pe"],
                region=Region.TR,
                locale="en",
            )
        assert isinstance(result, list)
        assert isinstance(result[0], StockHistoricalRatios)
        assert result[0].slug == "pe"
        assert result[0].final_value == 10.0
        assert result[0].three_year_growth == 0.15
        assert result[0].year_growth == 0.05
        assert result[0].final_sector_value == 11.0
        assert result[0].currency == Currency.TRY
        assert result[0].format == HistoricalRatiosFormat.DECIMAL
        assert result[0].name == "Price/Earnings"
        assert isinstance(result[0].items, list)

    @patch("httpx.Client")
    def test_get_historical_ratios_descriptions(self, mock_httpx_client):
        mock_response_data = [
            {
                "id": 1,
                "format": "decimal",
                "currency": "TRY",
                "slug": "pe",
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2023-01-02T00:00:00Z",
                "name": "Price/Earnings",
                "description": "PE ratio description",
                "locale": "en",
                "isRealtime": False,
            }
        ]
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            result = client.financials.get_historical_ratios_descriptions(
                locale="en",
                region=Region.TR,
            )
        assert isinstance(result, list)
        assert isinstance(result[0], StockHistoricalRatiosDescription)
        assert result[0].slug == "pe"
        assert result[0].name == "Price/Earnings"
        assert result[0].description == "PE ratio description"

    @patch("httpx.Client")
    def test_get_historical_financial_sheets(self, mock_httpx_client):
        mock_response_data = {
            "sheets": [
                {
                    "period": "2024-3",
                    "items": [
                        {
                            "description": "Finansal Varlıklar (Net)",
                            "value": 822843563000,
                            "lineCodeId": 15031,
                            "indentLevel": 0,
                        }
                    ],
                }
            ]
        }
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        from_date = FinancialSheetDate(year=2024, month=3, day=1)
        to_date = FinancialSheetDate(year=2024, month=3, day=31)
        with patch.object(client, "get", return_value=mock_response_data):
            result = client.financials.get_historical_financial_sheets(
                symbol="TUPRS",
                from_date=from_date,
                to_date=to_date,
                sheet_type=FinancialSheetType.BALANCE_SHEET,
                period=FinancialSheetPeriod.CUMULATIVE,
                currency=Currency.TRY,
                region=Region.TR,
            )
        assert isinstance(result, HistoricalFinancialSheets)
        assert isinstance(result.sheets, list)
        assert result.sheets[0].period == "2024-3"
        assert isinstance(result.sheets[0].items, list)
        assert result.sheets[0].items[0].description == "Finansal Varlıklar (Net)"
        assert result.sheets[0].items[0].value == 822843563000
        assert result.sheets[0].items[0].line_code_id == 15031
        assert result.sheets[0].items[0].indent_level == 0
