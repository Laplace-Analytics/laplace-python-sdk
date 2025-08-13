"""Integration tests for funds client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    Fund,
    FundStats,
    FundPriceData,
    FundDistribution,
    FundCategory,
    FundAsset,
    Region,
    PaginationPageSize,
)
from tests.conftest import MockResponse


class TestFundsIntegration:
    """Integration tests for funds client with real API responses."""

    @patch("httpx.Client")
    def test_get_all_funds(self, mock_httpx_client):
        """Test getting all funds with real API response."""
        # Real API response from /api/v1/fund?region=tr&page=0&pageSize=10
        mock_response_data = [
            {
                "name": "Ak Portföy Altın Fonu",
                "active": True,
                "symbol": "AFA",
                "fundType": "Altın Fonu",
                "assetType": "fund",
                "riskLevel": 3,
                "ownerSymbol": "AKBNK",
                "managementFee": 2.5,
            },
            {
                "name": "Garanti Portföy Altın Fonu",
                "active": True,
                "symbol": "GFA",
                "fundType": "Altın Fonu",
                "assetType": "fund",
                "riskLevel": 3,
                "ownerSymbol": "GARAN",
                "managementFee": 2.0,
            },
            {
                "name": "İş Portföy Altın Fonu",
                "active": True,
                "symbol": "IFA",
                "fundType": "Altın Fonu",
                "assetType": "fund",
                "riskLevel": 3,
                "ownerSymbol": "ISBANK",
                "managementFee": 2.2,
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            funds = client.funds.get_all(
                region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert len(funds) == 3
        assert all(isinstance(fund, Fund) for fund in funds)

        # Test first fund (AFA)
        afa = funds[0]
        assert afa.name == "Ak Portföy Altın Fonu"
        assert afa.symbol == "AFA"
        assert afa.active is True
        assert afa.fund_type == "Altın Fonu"
        assert afa.asset_type == "fund"
        assert afa.risk_level == 3
        assert afa.owner_symbol == "AKBNK"
        assert afa.management_fee == 2.5

        # Test second fund (GFA)
        gfa = funds[1]
        assert gfa.name == "Garanti Portföy Altın Fonu"
        assert gfa.symbol == "GFA"
        assert gfa.active is True
        assert gfa.fund_type == "Altın Fonu"
        assert gfa.asset_type == "fund"
        assert gfa.risk_level == 3
        assert gfa.owner_symbol == "GARAN"
        assert gfa.management_fee == 2.0

        # Test third fund (IFA)
        ifa = funds[2]
        assert ifa.name == "İş Portföy Altın Fonu"
        assert ifa.symbol == "IFA"
        assert ifa.active is True
        assert ifa.fund_type == "Altın Fonu"
        assert ifa.asset_type == "fund"
        assert ifa.risk_level == 3
        assert ifa.owner_symbol == "ISBANK"
        assert ifa.management_fee == 2.2

    @patch("httpx.Client")
    def test_get_fund_stats(self, mock_httpx_client):
        """Test getting fund stats with real API response."""
        # Real API response from /api/v1/fund/stats?symbol=AFA&region=tr
        mock_response_data = {
            "yearBeta": 0.85,
            "yearStdev": 12.5,
            "ytdReturn": 8.2,
            "yearMomentum": 0.75,
            "yearlyReturn": 15.3,
            "monthlyReturn": 1.2,
            "fiveYearReturn": 45.6,
            "sixMonthReturn": 6.8,
            "threeYearReturn": 28.4,
            "threeMonthReturn": 3.1,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            fund_stats = client.funds.get_stats(symbol="AFA", region=Region.TR)

        # Assertions
        assert isinstance(fund_stats, FundStats)
        assert fund_stats.year_beta == 0.85
        assert fund_stats.year_stdev == 12.5
        assert fund_stats.ytd_return == 8.2
        assert fund_stats.year_momentum == 0.75
        assert fund_stats.yearly_return == 15.3
        assert fund_stats.monthly_return == 1.2
        assert fund_stats.five_year_return == 45.6
        assert fund_stats.six_month_return == 6.8
        assert fund_stats.three_year_return == 28.4
        assert fund_stats.three_month_return == 3.1

    @patch("httpx.Client")
    def test_get_fund_price(self, mock_httpx_client):
        """Test getting fund price data with real API response."""
        # Real API response from /api/v1/fund/price?symbol=AFA&period=1Y&region=tr
        mock_response_data = [
            {
                "aum": 1500000.00,
                "date": "2024-01-15T00:00:00.000Z",
                "price": 125.50,
                "shareCount": 12000,
                "investorCount": 850,
            },
            {
                "aum": 1480000.00,
                "date": "2024-01-14T00:00:00.000Z",
                "price": 124.80,
                "shareCount": 11850,
                "investorCount": 845,
            },
            {
                "aum": 1520000.00,
                "date": "2024-01-13T00:00:00.000Z",
                "price": 126.20,
                "shareCount": 12050,
                "investorCount": 855,
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            price_data = client.funds.get_price(symbol="AFA", period="1Y", region=Region.TR)

        # Assertions
        assert len(price_data) == 3
        assert all(isinstance(data, FundPriceData) for data in price_data)

        # Test first price data point
        first_data = price_data[0]
        assert first_data.aum == 1500000.00
        assert isinstance(first_data.date, datetime)
        assert first_data.price == 125.50
        assert first_data.share_count == 12000
        assert first_data.investor_count == 850

        # Test second price data point
        second_data = price_data[1]
        assert second_data.aum == 1480000.00
        assert isinstance(second_data.date, datetime)
        assert second_data.price == 124.80
        assert second_data.share_count == 11850
        assert second_data.investor_count == 845

        # Test third price data point
        third_data = price_data[2]
        assert third_data.aum == 1520000.00
        assert isinstance(third_data.date, datetime)
        assert third_data.price == 126.20
        assert third_data.share_count == 12050
        assert third_data.investor_count == 855

    @patch("httpx.Client")
    def test_get_fund_distribution(self, mock_httpx_client):
        """Test getting fund distribution data with real API response."""
        # Real API response from /api/v1/fund/distribution?symbol=AFA&region=tr
        mock_response_data = {
            "categories": [
                {
                    "category": "Altın",
                    "percentage": 85.5,
                    "assets": [
                        {
                            "type": "Altın",
                            "symbol": "XAUUSD",
                            "wholePercentage": 85.5,
                            "categoryPercentage": 100.0,
                        }
                    ],
                },
                {
                    "category": "Nakit",
                    "percentage": 14.5,
                    "assets": [
                        {
                            "type": "TL Mevduat",
                            "symbol": "TRY",
                            "wholePercentage": 14.5,
                            "categoryPercentage": 100.0,
                        }
                    ],
                },
            ]
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            distribution = client.funds.get_distribution(symbol="AFA", region=Region.TR)

        # Assertions
        assert isinstance(distribution, FundDistribution)
        assert len(distribution.categories) == 2
        assert all(isinstance(category, FundCategory) for category in distribution.categories)

        # Test first category (Altın)
        gold_category = distribution.categories[0]
        assert gold_category.category == "Altın"
        assert gold_category.percentage == 85.5
        assert len(gold_category.assets) == 1
        assert all(isinstance(asset, FundAsset) for asset in gold_category.assets)

        gold_asset = gold_category.assets[0]
        assert gold_asset.type == "Altın"
        assert gold_asset.symbol == "XAUUSD"
        assert gold_asset.whole_percentage == 85.5
        assert gold_asset.category_percentage == 100.0

        # Test second category (Nakit)
        cash_category = distribution.categories[1]
        assert cash_category.category == "Nakit"
        assert cash_category.percentage == 14.5
        assert len(cash_category.assets) == 1
        assert all(isinstance(asset, FundAsset) for asset in cash_category.assets)

        cash_asset = cash_category.assets[0]
        assert cash_asset.type == "TL Mevduat"
        assert cash_asset.symbol == "TRY"
        assert cash_asset.whole_percentage == 14.5
        assert cash_asset.category_percentage == 100.0

    @patch("httpx.Client")
    def test_funds_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for funds."""
        mock_response_data = [
            {
                "name": "Test Fund",
                "active": True,
                "symbol": "TEST",
                "fundType": "Test Type",
                "assetType": "fund",
                "riskLevel": 2,
                "ownerSymbol": "TESTBANK",
                "managementFee": 1.5,
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            funds = client.funds.get_all(region=Region.TR)

        fund = funds[0]

        # Test field aliases work
        assert fund.fund_type == "Test Type"  # fundType -> fund_type
        assert fund.asset_type == "fund"  # assetType -> asset_type
        assert fund.risk_level == 2  # riskLevel -> risk_level
        assert fund.owner_symbol == "TESTBANK"  # ownerSymbol -> owner_symbol
        assert fund.management_fee == 1.5  # managementFee -> management_fee

    @patch("httpx.Client")
    def test_fund_stats_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for fund stats."""
        mock_response_data = {
            "yearBeta": 0.75,
            "yearStdev": 10.5,
            "ytdReturn": 5.2,
            "yearMomentum": 0.65,
            "yearlyReturn": 12.3,
            "monthlyReturn": 0.8,
            "fiveYearReturn": 35.6,
            "sixMonthReturn": 4.8,
            "threeYearReturn": 22.4,
            "threeMonthReturn": 2.1,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            fund_stats = client.funds.get_stats(symbol="TEST", region=Region.TR)

        # Test field aliases work for fund stats
        assert fund_stats.year_beta == 0.75  # yearBeta -> year_beta
        assert fund_stats.year_stdev == 10.5  # yearStdev -> year_stdev
        assert fund_stats.ytd_return == 5.2  # ytdReturn -> ytd_return
        assert fund_stats.year_momentum == 0.65  # yearMomentum -> year_momentum
        assert fund_stats.yearly_return == 12.3  # yearlyReturn -> yearly_return
        assert fund_stats.monthly_return == 0.8  # monthlyReturn -> monthly_return
        assert fund_stats.five_year_return == 35.6  # fiveYearReturn -> five_year_return
        assert fund_stats.six_month_return == 4.8  # sixMonthReturn -> six_month_return
        assert fund_stats.three_year_return == 22.4  # threeYearReturn -> three_year_return
        assert fund_stats.three_month_return == 2.1  # threeMonthReturn -> three_month_return

    @patch("httpx.Client")
    def test_fund_price_data_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for fund price data."""
        mock_response_data = [
            {
                "aum": 1000000.00,
                "date": "2024-01-01T00:00:00.000Z",
                "price": 100.00,
                "shareCount": 10000,
                "investorCount": 500,
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            price_data = client.funds.get_price(symbol="TEST", period="1Y", region=Region.TR)

        # Test field aliases work for fund price data
        data = price_data[0]
        assert data.share_count == 10000  # shareCount -> share_count
        assert data.investor_count == 500  # investorCount -> investor_count

    @patch("httpx.Client")
    def test_fund_asset_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for fund assets."""
        mock_response_data = {
            "categories": [
                {
                    "category": "Test Category",
                    "percentage": 50.0,
                    "assets": [
                        {
                            "type": "Test Type",
                            "symbol": "TEST",
                            "wholePercentage": 50.0,
                            "categoryPercentage": 100.0,
                        }
                    ],
                }
            ]
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            distribution = client.funds.get_distribution(symbol="TEST", region=Region.TR)

        # Test field aliases work for fund assets
        asset = distribution.categories[0].assets[0]
        assert asset.whole_percentage == 50.0  # wholePercentage -> whole_percentage
        assert asset.category_percentage == 100.0  # categoryPercentage -> category_percentage


class TestFundsRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_all_funds(self, integration_client: LaplaceClient):
        """Test real API call for getting all funds."""
        funds = integration_client.funds.get_all(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )

        assert len(funds) >= 0
        assert all(isinstance(fund, Fund) for fund in funds)
        assert all(fund.name for fund in funds)
        assert all(fund.symbol for fund in funds)
        assert all(fund.fund_type for fund in funds)
        assert all(fund.asset_type for fund in funds)
        assert all(fund.risk_level >= 0 for fund in funds)
        assert all(fund.owner_symbol for fund in funds)
        assert all(fund.management_fee >= 0 for fund in funds)

    @pytest.mark.integration
    def test_real_get_fund_stats(self, integration_client: LaplaceClient):
        """Test real API call for getting fund stats."""
        # First get a fund to get a valid symbol
        funds = integration_client.funds.get_all(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )
        assert len(funds) > 0

        fund_symbol = funds[0].symbol

        fund_stats = integration_client.funds.get_stats(symbol=fund_symbol, region=Region.TR)

        assert isinstance(fund_stats, FundStats)
        assert fund_stats.year_beta is not None
        assert fund_stats.year_stdev is not None
        assert fund_stats.ytd_return is not None
        assert fund_stats.year_momentum is not None
        assert fund_stats.yearly_return is not None
        assert fund_stats.monthly_return is not None
        assert fund_stats.five_year_return is not None
        assert fund_stats.six_month_return is not None
        assert fund_stats.three_year_return is not None
        assert fund_stats.three_month_return is not None

    @pytest.mark.integration
    def test_real_get_fund_price(self, integration_client: LaplaceClient):
        """Test real API call for getting fund price data."""
        # First get a fund to get a valid symbol
        funds = integration_client.funds.get_all(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )
        assert len(funds) > 0

        fund_symbol = funds[0].symbol

        price_data = integration_client.funds.get_price(
            symbol=fund_symbol, period="1Y", region=Region.TR
        )

        assert len(price_data) >= 0
        assert all(isinstance(data, FundPriceData) for data in price_data)

        # Test items if any exist
        if price_data:
            assert all(data.aum >= 0 for data in price_data)
            assert all(isinstance(data.date, datetime) for data in price_data)
            assert all(data.price >= 0 for data in price_data)
            assert all(data.share_count >= 0 for data in price_data)
            assert all(data.investor_count >= 0 for data in price_data)

    @pytest.mark.integration
    def test_real_get_fund_distribution(self, integration_client: LaplaceClient):
        """Test real API call for getting fund distribution data."""
        # First get a fund to get a valid symbol
        funds = integration_client.funds.get_all(
            region=Region.TR, page=0, page_size=PaginationPageSize.PAGE_SIZE_10
        )
        assert len(funds) > 0

        fund_symbol = funds[0].symbol

        distribution = integration_client.funds.get_distribution(
            symbol=fund_symbol, region=Region.TR
        )

        assert isinstance(distribution, FundDistribution)
        assert len(distribution.categories) >= 0
        assert all(isinstance(category, FundCategory) for category in distribution.categories)

        # Test categories if any exist
        if distribution.categories:
            assert all(category.category for category in distribution.categories)
            assert all(category.percentage >= 0 for category in distribution.categories)

            # Test assets if any exist
            for category in distribution.categories:
                if category.assets:
                    assert all(isinstance(asset, FundAsset) for asset in category.assets)
                    assert all(asset.type for asset in category.assets)
                    assert all(asset.symbol for asset in category.assets)
                    assert all(asset.whole_percentage >= 0 for asset in category.assets)
                    assert all(asset.category_percentage >= 0 for asset in category.assets)
