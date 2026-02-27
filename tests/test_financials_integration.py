"""Integration tests for financials client."""

from datetime import datetime
from typing import get_args
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    Currency,
    FinancialSheetDate,
    FinancialSheetPeriod,
    FinancialSheetType,
    HistoricalFinancialSheet,
    HistoricalFinancialSheetRow,
    HistoricalFinancialSheets,
    HistoricalRatiosFormat,
    Locale,
    RatioComparisonPeerType,
    Region,
    StockHistoricalRatios,
    StockHistoricalRatiosData,
    StockHistoricalRatiosDescription,
    StockPeerFinancialRatioComparison,
    StockPeerFinancialRatioComparisonData,
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
                "items": [{"period": "2023-1", "value": 10.0, "sectorMean": 11.0}],
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
        assert isinstance(result[0].items[0], StockHistoricalRatiosData)

        first_item = result[0].items[0]

        assert first_item.period == "2023-1"
        assert first_item.value == 10.0
        assert first_item.sector_mean == 11.0


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

        assert result[0].id == 1
        assert result[0].slug == "pe"
        assert result[0].name == "Price/Earnings"
        assert result[0].description == "PE ratio description"
        assert isinstance(result[0].created_at, datetime)
        assert isinstance(result[0].updated_at, datetime)
        assert result[0].format == "decimal"
        assert result[0].locale == "en"
        assert result[0].currency == Currency.TRY
        assert result[0].is_realtime == False

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
        assert isinstance(result.sheets[0], HistoricalFinancialSheet)
        assert result.sheets[0].period == "2024-3"
        assert isinstance(result.sheets[0].items, list)
        assert isinstance(result.sheets[0].items[0], HistoricalFinancialSheetRow)
        assert result.sheets[0].items[0].description == "Finansal Varlıklar (Net)"
        assert result.sheets[0].items[0].value == 822843563000
        assert result.sheets[0].items[0].line_code_id == 15031
        assert result.sheets[0].items[0].indent_level == 0


class TestFinancialsRealIntegration:
    """Real integration tests for financials (requires API key)."""

    @pytest.mark.integration
    def test_real_get_financial_ratio_comparison(self, integration_client: LaplaceClient):
        """Test real API call for financial ratio comparison."""
        result = integration_client.financials.get_financial_ratio_comparison(
            symbol="THYAO",
            region=Region.TR,
            peer_type=RatioComparisonPeerType.INDUSTRY,
        )

        assert isinstance(result, list)

        if result:
            assert isinstance(result[0], StockPeerFinancialRatioComparison)

            assert isinstance(result[0].metric_name, str)
            assert len(result[0].metric_name) > 0
            assert isinstance(result[0].normalized_value, float)
            assert isinstance(result[0].data, list)

            assert isinstance(result[0].data[0], StockPeerFinancialRatioComparisonData)
            assert isinstance(result[0].data[0].slug, str)
            assert len(result[0].data[0].slug) > 0
            assert isinstance(result[0].data[0].value, float)
            assert isinstance(result[0].data[0].average, float)

    @pytest.mark.integration
    def test_real_get_historical_ratios(self, integration_client: LaplaceClient):
        """Test real API call for historical ratios."""
        requested_keys = ["pe", "pb"]
        result = integration_client.financials.get_historical_ratios(
            symbol="THYAO",
            keys=requested_keys,
            region=Region.TR
        )

        assert isinstance(result, list)
        
        if result:
            ratio = result[0]
            assert isinstance(ratio, StockHistoricalRatios)
            
            assert isinstance(ratio.slug, str)
            assert ratio.slug in requested_keys
            assert isinstance(ratio.name, str)
            assert len(ratio.name) > 0
            
            assert isinstance(ratio.final_value, float)
            assert isinstance(ratio.three_year_growth, float)
            assert isinstance(ratio.year_growth, float)
            assert isinstance(ratio.final_sector_value, float)
            
            assert isinstance(ratio.currency, Currency)
            assert isinstance(ratio.format, HistoricalRatiosFormat)
            
            assert isinstance(ratio.items, list)
            if ratio.items:
                first_data_point = ratio.items[0]
                assert isinstance(first_data_point, StockHistoricalRatiosData)
                
                assert isinstance(first_data_point.period, str)
                assert len(first_data_point.period) >= 4 
                
                assert isinstance(first_data_point.value, float)
                assert isinstance(first_data_point.sector_mean, float)

    @pytest.mark.integration
    def test_real_get_historical_ratios_descriptions(self, integration_client: LaplaceClient):
        """Test real API call for historical ratios descriptions."""
        result = integration_client.financials.get_historical_ratios_descriptions(
            region=Region.TR,
            locale="tr"
        )

        assert isinstance(result, list)
        if result:
            desc = result[0]
            assert isinstance(desc, StockHistoricalRatiosDescription)
            
            assert isinstance(desc.id, int)
            assert isinstance(desc.slug, str)
            assert len(desc.slug) > 0
            assert isinstance(desc.name, str)
            assert len(desc.name) > 0
            assert isinstance(desc.description, str)
            assert len(desc.description) > 0
            
            assert isinstance(desc.created_at, datetime)
            assert isinstance(desc.updated_at, datetime)
            
            assert desc.locale in get_args(Locale)
            assert isinstance(desc.is_realtime, bool)
            
            assert isinstance(desc.format, str)
            assert isinstance(desc.currency, Currency)

    @pytest.mark.integration
    def test_real_get_historical_financial_sheets(self, integration_client: LaplaceClient):
        """Test real API call for historical financial sheets."""
        from_date = FinancialSheetDate(year=2023, month=1, day=1)
        to_date = FinancialSheetDate(year=2024, month=1, day=1)
        
        result = integration_client.financials.get_historical_financial_sheets(
            symbol="THYAO",
            from_date=from_date,
            to_date=to_date,
            sheet_type=FinancialSheetType.BALANCE_SHEET,
            period=FinancialSheetPeriod.CUMULATIVE,
            region=Region.TR,
            currency=Currency.TRY
        )

        assert isinstance(result, HistoricalFinancialSheets)
        assert isinstance(result.sheets, list)
        
        if result.sheets:
            sheet = result.sheets[0]
            assert isinstance(sheet, HistoricalFinancialSheet)
            assert isinstance(sheet.period, str)
            assert len(sheet.period) > 0
            assert isinstance(sheet.items, list)
            
            if sheet.items:
                row = sheet.items[0]
                assert isinstance(row, HistoricalFinancialSheetRow)
                
                assert isinstance(row.description, str)
                assert len(row.description) > 0
                assert isinstance(row.value, (float, int))
                assert isinstance(row.line_code_id, int)
                assert isinstance(row.indent_level, int)
                assert row.indent_level >= 0