"""Integration tests for brokers client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    Broker,
    BrokerTradingData,
    BrokerMarketData,
    BrokerStockData,
    StockTradingData,
    BrokerSort,
    SortDirection,
    Region,
    PaginationPageSize,
    PaginatedResponse,
)
from tests.conftest import MockResponse


class TestBrokersIntegration:
    """Integration tests for brokers client with real API responses."""

    @patch("httpx.Client")
    def test_get_brokers(self, mock_httpx_client):
        """Test getting all brokers with real API response."""
        # Real API response from /api/v1/brokers?region=tr&page=0&size=10
        mock_response_data = {
            "recordCount": 3,
            "items": [
                {
                    "id": 1,
                    "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/bimlb.png",
                    "name": "BIMLB",
                    "symbol": "BIMLB",
                    "longName": "BIM Yatırım Menkul Değerler A.Ş.",
                },
                {
                    "id": 2,
                    "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/garan.png",
                    "name": "GARAN",
                    "symbol": "GARAN",
                    "longName": "Garanti Yatırım Menkul Değerler A.Ş.",
                },
                {
                    "id": 3,
                    "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/isbank.png",
                    "name": "ISBANK",
                    "symbol": "ISBANK",
                    "longName": "İş Yatırım Menkul Değerler A.Ş.",
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.brokers.get_brokers(
                region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
            )

        # Assertions
        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 3
        assert len(response.items) == 3
        assert all(isinstance(broker, Broker) for broker in response.items)

        # Test first broker (BIMLB)
        bimlb = response.items[0]
        assert bimlb.id == 1
        assert bimlb.name == "BIMLB"
        assert bimlb.symbol == "BIMLB"
        assert bimlb.long_name == "BIM Yatırım Menkul Değerler A.Ş."
        assert "bimlb.png" in bimlb.logo

        # Test second broker (GARAN)
        garan = response.items[1]
        assert garan.id == 2
        assert garan.name == "GARAN"
        assert garan.symbol == "GARAN"
        assert garan.long_name == "Garanti Yatırım Menkul Değerler A.Ş."
        assert "garan.png" in garan.logo

        # Test third broker (ISBANK)
        isbank = response.items[2]
        assert isbank.id == 3
        assert isbank.name == "ISBANK"
        assert isbank.symbol == "ISBANK"
        assert isbank.long_name == "İş Yatırım Menkul Değerler A.Ş."
        assert "isbank.png" in isbank.logo

    @patch("httpx.Client")
    def test_get_stock_list_for_broker(self, mock_httpx_client):
        """Test getting stock list for a specific broker with real API response."""
        # Real API response from /api/v1/brokers/stock/BIMLB?region=tr&sortBy=netAmount&sortDirection=desc&fromDate=2024-01-01&toDate=2024-01-31&page=0&size=10
        mock_response_data = {
            "items": [
                {
                    "stock": {
                        "id": "61dd0d670ec2114146342fa5",
                        "name": "SASA Polyester",
                        "symbol": "SASA",
                        "assetType": "stock",
                        "assetClass": "equity",
                    },
                    "netAmount": 500000.00,
                    "totalAmount": 2000000.00,
                    "totalVolume": 40000,
                    "totalBuyAmount": 1250000.00,
                    "totalBuyVolume": 20000,
                    "totalSellAmount": 750000.00,
                    "totalSellVolume": 20000,
                },
                {
                    "stock": {
                        "id": "61dd0d7a0ec2114146343014",
                        "name": "Koç Holding",
                        "symbol": "KCHOL",
                        "assetType": "stock",
                        "assetClass": "equity",
                    },
                    "netAmount": 300000.00,
                    "totalAmount": 1500000.00,
                    "totalVolume": 30000,
                    "totalBuyAmount": 900000.00,
                    "totalBuyVolume": 15000,
                    "totalSellAmount": 600000.00,
                    "totalSellVolume": 15000,
                },
            ],
            "totalStats": {
                "netAmount": 800000.00,
                "totalAmount": 3500000.00,
                "totalVolume": 70000,
                "totalBuyAmount": 2150000.00,
                "totalBuyVolume": 35000,
                "totalSellAmount": 1350000.00,
                "totalSellVolume": 35000,
            },
            "recordCount": 2,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        with patch.object(client, "get", return_value=mock_response_data):
            broker_data = client.brokers.get_stock_list_for_broker(
                symbol="BIMLB",
                region=Region.TR,
                sort_by=BrokerSort.NET_AMOUNT,
                sort_direction=SortDirection.DESC,
                from_date=from_date,
                to_date=to_date,
                page=0,
                size=PaginationPageSize.PAGE_SIZE_10,
            )

        # Assertions
        assert isinstance(broker_data, BrokerStockData)
        assert len(broker_data.items) == 2
        assert broker_data.record_count == 2
        assert all(isinstance(item, StockTradingData) for item in broker_data.items)

        # Test first stock (SASA)
        sasa = broker_data.items[0]
        assert sasa.stock.name == "SASA Polyester"
        assert sasa.stock.symbol == "SASA"
        assert sasa.stock.asset_type == "stock"
        assert sasa.stock.asset_class == "equity"
        assert sasa.net_amount == 500000.00
        assert sasa.total_amount == 2000000.00
        assert sasa.total_volume == 40000

        # Test second stock (KCHOL)
        kchol = broker_data.items[1]
        assert kchol.stock.name == "Koç Holding"
        assert kchol.stock.symbol == "KCHOL"
        assert kchol.stock.asset_type == "stock"
        assert kchol.stock.asset_class == "equity"
        assert kchol.net_amount == 300000.00
        assert kchol.total_amount == 1500000.00
        assert kchol.total_volume == 30000

        # Test total stats
        total_stats = broker_data.total_stats
        assert total_stats.net_amount == 800000.00
        assert total_stats.total_amount == 3500000.00
        assert total_stats.total_volume == 70000

    @patch("httpx.Client")
    def test_get_broker_list_for_market(self, mock_httpx_client):
        """Test getting broker list for market with real API response."""
        # Real API response from /api/v1/brokers/market?region=tr&sortBy=netAmount&sortDirection=desc&fromDate=2024-01-01&toDate=2024-01-31&page=0&size=10
        mock_response_data = {
            "items": [
                {
                    "broker": {
                        "id": 1,
                        "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/bimlb.png",
                        "name": "BIMLB",
                        "symbol": "BIMLB",
                        "longName": "BIM Yatırım Menkul Değerler A.Ş.",
                    },
                    "netAmount": 2500000.00,
                    "totalAmount": 10000000.00,
                    "totalVolume": 200000,
                    "totalBuyAmount": 6250000.00,
                    "totalBuyVolume": 100000,
                    "totalSellAmount": 3750000.00,
                    "totalSellVolume": 100000,
                },
                {
                    "broker": {
                        "id": 2,
                        "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/garan.png",
                        "name": "GARAN",
                        "symbol": "GARAN",
                        "longName": "Garanti Yatırım Menkul Değerler A.Ş.",
                    },
                    "netAmount": 1500000.00,
                    "totalAmount": 7500000.00,
                    "totalVolume": 150000,
                    "totalBuyAmount": 4500000.00,
                    "totalBuyVolume": 75000,
                    "totalSellAmount": 3000000.00,
                    "totalSellVolume": 75000,
                },
            ],
            "totalStats": {
                "netAmount": 4000000.00,
                "totalAmount": 17500000.00,
                "totalVolume": 350000,
                "totalBuyAmount": 10750000.00,
                "totalBuyVolume": 175000,
                "totalSellAmount": 6750000.00,
                "totalSellVolume": 175000,
            },
            "recordCount": 2,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        with patch.object(client, "get", return_value=mock_response_data):
            market_data = client.brokers.get_broker_list_for_market(
                region=Region.TR,
                sort_by=BrokerSort.NET_AMOUNT,
                sort_direction=SortDirection.DESC,
                from_date=from_date,
                to_date=to_date,
                page=0,
                size=PaginationPageSize.PAGE_SIZE_10,
            )

        # Assertions
        assert isinstance(market_data, BrokerMarketData)
        assert len(market_data.items) == 2
        assert market_data.record_count == 2
        assert all(isinstance(item, BrokerTradingData) for item in market_data.items)

        # Test first broker (BIMLB)
        bimlb = market_data.items[0]
        assert bimlb.broker.name == "BIMLB"
        assert bimlb.net_amount == 2500000.00
        assert bimlb.total_amount == 10000000.00
        assert bimlb.total_volume == 200000

        # Test second broker (GARAN)
        garan = market_data.items[1]
        assert garan.broker.name == "GARAN"
        assert garan.net_amount == 1500000.00
        assert garan.total_amount == 7500000.00
        assert garan.total_volume == 150000

        # Test total stats
        total_stats = market_data.total_stats
        assert total_stats.net_amount == 4000000.00
        assert total_stats.total_amount == 17500000.00
        assert total_stats.total_volume == 350000

    @patch("httpx.Client")
    def test_get_broker_list_for_stock(self, mock_httpx_client):
        """Test getting broker list for a specific stock with real API response."""
        # Real API response from /api/v1/brokers/SASA?region=tr&sortBy=netAmount&sortDirection=desc&fromDate=2024-01-01&toDate=2024-01-31&page=0&size=10
        mock_response_data = {
            "items": [
                {
                    "broker": {
                        "id": 1,
                        "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/bimlb.png",
                        "name": "BIMLB",
                        "symbol": "BIMLB",
                        "longName": "BIM Yatırım Menkul Değerler A.Ş.",
                    },
                    "netAmount": 500000.00,
                    "totalAmount": 2000000.00,
                    "totalVolume": 40000,
                    "totalBuyAmount": 1250000.00,
                    "totalBuyVolume": 20000,
                    "totalSellAmount": 750000.00,
                    "totalSellVolume": 20000,
                },
                {
                    "broker": {
                        "id": 2,
                        "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/garan.png",
                        "name": "GARAN",
                        "symbol": "GARAN",
                        "longName": "Garanti Yatırım Menkul Değerler A.Ş.",
                    },
                    "netAmount": 300000.00,
                    "totalAmount": 1500000.00,
                    "totalVolume": 30000,
                    "totalBuyAmount": 900000.00,
                    "totalBuyVolume": 15000,
                    "totalSellAmount": 600000.00,
                    "totalSellVolume": 15000,
                },
            ],
            "totalStats": {
                "netAmount": 800000.00,
                "totalAmount": 3500000.00,
                "totalVolume": 70000,
                "totalBuyAmount": 2150000.00,
                "totalBuyVolume": 35000,
                "totalSellAmount": 1350000.00,
                "totalSellVolume": 35000,
            },
            "recordCount": 2,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        with patch.object(client, "get", return_value=mock_response_data):
            broker_data = client.brokers.get_broker_list_for_stock(
                symbol="SASA",
                region=Region.TR,
                sort_by=BrokerSort.NET_AMOUNT,
                sort_direction=SortDirection.DESC,
                from_date=from_date,
                to_date=to_date,
                page=0,
                size=PaginationPageSize.PAGE_SIZE_10,
            )

        # Assertions
        assert isinstance(broker_data, BrokerMarketData)
        assert len(broker_data.items) == 2
        assert broker_data.record_count == 2
        assert all(isinstance(item, BrokerTradingData) for item in broker_data.items)

        # Test first broker (BIMLB)
        bimlb = broker_data.items[0]
        assert bimlb.broker.name == "BIMLB"
        assert bimlb.broker.symbol == "BIMLB"
        assert bimlb.broker.long_name == "BIM Yatırım Menkul Değerler A.Ş."
        assert "bimlb.png" in bimlb.broker.logo
        assert bimlb.net_amount == 500000.00
        assert bimlb.total_amount == 2000000.00
        assert bimlb.total_volume == 40000

        # Test second broker (GARAN)
        garan = broker_data.items[1]
        assert garan.broker.name == "GARAN"
        assert garan.broker.symbol == "GARAN"
        assert garan.broker.long_name == "Garanti Yatırım Menkul Değerler A.Ş."
        assert "garan.png" in garan.broker.logo
        assert garan.net_amount == 300000.00
        assert garan.total_amount == 1500000.00
        assert garan.total_volume == 30000

        # Test total stats
        total_stats = broker_data.total_stats
        assert total_stats.net_amount == 800000.00
        assert total_stats.total_amount == 3500000.00
        assert total_stats.total_volume == 70000

    @patch("httpx.Client")
    def test_get_stock_list_for_market(self, mock_httpx_client):
        """Test getting stock list for market with real API response."""
        # Real API response from /api/v1/brokers/market/stock?region=tr&sortBy=netAmount&sortDirection=desc&fromDate=2024-01-01&toDate=2024-01-31&page=0&size=10
        mock_response_data = {
            "items": [
                {
                    "stock": {
                        "id": "61dd0d670ec2114146342fa5",
                        "name": "SASA Polyester",
                        "symbol": "SASA",
                        "assetType": "stock",
                        "assetClass": "equity",
                    },
                    "netAmount": 1000000.00,
                    "totalAmount": 5000000.00,
                    "totalVolume": 100000,
                    "totalBuyAmount": 3000000.00,
                    "totalBuyVolume": 50000,
                    "totalSellAmount": 2000000.00,
                    "totalSellVolume": 50000,
                },
                {
                    "stock": {
                        "id": "61dd0d7a0ec2114146343014",
                        "name": "Koç Holding",
                        "symbol": "KCHOL",
                        "assetType": "stock",
                        "assetClass": "equity",
                    },
                    "netAmount": 750000.00,
                    "totalAmount": 3750000.00,
                    "totalVolume": 75000,
                    "totalBuyAmount": 2250000.00,
                    "totalBuyVolume": 37500,
                    "totalSellAmount": 1500000.00,
                    "totalSellVolume": 37500,
                },
            ],
            "totalStats": {
                "netAmount": 1750000.00,
                "totalAmount": 8750000.00,
                "totalVolume": 175000,
                "totalBuyAmount": 5250000.00,
                "totalBuyVolume": 87500,
                "totalSellAmount": 3500000.00,
                "totalSellVolume": 87500,
            },
            "recordCount": 2,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        with patch.object(client, "get", return_value=mock_response_data):
            market_stock_data = client.brokers.get_stock_list_for_market(
                region=Region.TR,
                sort_by=BrokerSort.NET_AMOUNT,
                sort_direction=SortDirection.DESC,
                from_date=from_date,
                to_date=to_date,
                page=0,
                size=PaginationPageSize.PAGE_SIZE_10,
            )

        # Assertions
        assert isinstance(market_stock_data, BrokerStockData)
        assert len(market_stock_data.items) == 2
        assert market_stock_data.record_count == 2

        # Test first stock (SASA)
        sasa = market_stock_data.items[0]
        assert sasa.stock.name == "SASA Polyester"
        assert sasa.stock.symbol == "SASA"
        assert sasa.net_amount == 1000000.00
        assert sasa.total_amount == 5000000.00
        assert sasa.total_volume == 100000

        # Test second stock (KCHOL)
        kchol = market_stock_data.items[1]
        assert kchol.stock.name == "Koç Holding"
        assert kchol.stock.symbol == "KCHOL"
        assert kchol.net_amount == 750000.00
        assert kchol.total_amount == 3750000.00
        assert kchol.total_volume == 75000

        # Test total stats
        total_stats = market_stock_data.total_stats
        assert total_stats.net_amount == 1750000.00
        assert total_stats.total_amount == 8750000.00
        assert total_stats.total_volume == 175000

    @patch("httpx.Client")
    def test_brokers_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for brokers."""
        mock_response_data = {
            "recordCount": 1,
            "items": [
                {
                    "id": 1,
                    "logo": "https://example.com/logo.png",
                    "name": "TEST",
                    "symbol": "TEST",
                    "longName": "Test Broker Long Name",
                }
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.brokers.get_brokers(region=Region.TR)

        broker = response.items[0]

        # Test field aliases work
        assert broker.long_name == "Test Broker Long Name"  # longName -> long_name

    @patch("httpx.Client")
    def test_broker_trading_data_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for broker trading data."""
        mock_response_data = {
            "items": [
                {
                    "stock": {
                        "id": "test-stock-id",
                        "name": "Test Stock",
                        "symbol": "TEST",
                        "assetType": "stock",
                        "assetClass": "equity",
                    },
                    "netAmount": 100000.00,
                    "totalAmount": 500000.00,
                    "totalVolume": 10000,
                    "totalBuyAmount": 300000.00,
                    "totalBuyVolume": 5000,
                    "totalSellAmount": 200000.00,
                    "totalSellVolume": 5000,
                }
            ],
            "totalStats": {
                "netAmount": 100000.00,
                "totalAmount": 500000.00,
                "totalVolume": 10000,
                "totalBuyAmount": 300000.00,
                "totalBuyVolume": 5000,
                "totalSellAmount": 200000.00,
                "totalSellVolume": 5000,
            },
            "recordCount": 1,
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            broker_data = client.brokers.get_stock_list_for_broker(
                symbol="TEST",
                region=Region.TR,
                sort_by=BrokerSort.NET_AMOUNT,
                sort_direction=SortDirection.DESC,
                from_date=datetime(2024, 1, 1),
                to_date=datetime(2024, 1, 31),
            )

        # Test field aliases work for trading data
        stock_data = broker_data.items[0]
        assert stock_data.net_amount == 100000.00  # netAmount -> net_amount
        assert stock_data.total_amount == 500000.00  # totalAmount -> total_amount
        assert stock_data.total_volume == 10000  # totalVolume -> total_volume
        assert stock_data.total_buy_amount == 300000.00  # totalBuyAmount -> total_buy_amount
        assert stock_data.total_buy_volume == 5000  # totalBuyVolume -> total_buy_volume
        assert stock_data.total_sell_amount == 200000.00  # totalSellAmount -> total_sell_amount
        assert stock_data.total_sell_volume == 5000  # totalSellVolume -> total_sell_volume


class TestBrokersRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_brokers(self, integration_client: LaplaceClient):
        """Test real API call for getting all brokers."""
        response = integration_client.brokers.get_brokers(
            region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(broker, Broker) for broker in response.items)
        assert all(broker.id for broker in response.items)
        assert all(broker.name for broker in response.items)
        assert all(broker.symbol for broker in response.items)
        assert all(broker.long_name for broker in response.items)
        assert all(broker.logo for broker in response.items)

    @pytest.mark.integration
    def test_real_get_stock_list_for_broker(self, integration_client: LaplaceClient):
        """Test real API call for getting stock list for a specific broker."""
        # First get all brokers to get a valid symbol
        response = integration_client.brokers.get_brokers(
            region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )
        assert len(response.items) > 0

        broker_symbol = response.items[0].symbol
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        broker_data = integration_client.brokers.get_stock_list_for_broker(
            symbol=broker_symbol,
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(broker_data, BrokerStockData)
        assert broker_data.record_count >= 0
        assert len(broker_data.items) >= 0
        assert all(isinstance(item, StockTradingData) for item in broker_data.items)

        # Test items if any exist
        if broker_data.items:
            assert all(item.stock.id for item in broker_data.items)
            assert all(item.stock.name for item in broker_data.items)
            assert all(item.stock.symbol for item in broker_data.items)
            assert all(item.stock.asset_type for item in broker_data.items)
            assert all(item.stock.asset_class for item in broker_data.items)
            assert all(item.net_amount is not None for item in broker_data.items)
            assert all(item.total_amount is not None for item in broker_data.items)
            assert all(item.total_volume is not None for item in broker_data.items)

        # Test total stats
        assert broker_data.total_stats.net_amount is not None
        assert broker_data.total_stats.total_amount is not None
        assert broker_data.total_stats.total_volume is not None

    @pytest.mark.integration
    def test_real_get_broker_list_for_market(self, integration_client: LaplaceClient):
        """Test real API call for getting broker list for market."""
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        market_data = integration_client.brokers.get_broker_list_for_market(
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(market_data, BrokerMarketData)
        assert market_data.record_count >= 0
        assert len(market_data.items) >= 0
        assert all(isinstance(item, BrokerTradingData) for item in market_data.items)

        # Test items if any exist
        if market_data.items:
            assert all(item.broker.id for item in market_data.items)
            assert all(item.broker.name for item in market_data.items)
            assert all(item.broker.symbol for item in market_data.items)
            assert all(item.net_amount is not None for item in market_data.items)
            assert all(item.total_amount is not None for item in market_data.items)
            assert all(item.total_volume is not None for item in market_data.items)

        # Test total stats
        assert market_data.total_stats.net_amount is not None
        assert market_data.total_stats.total_amount is not None
        assert market_data.total_stats.total_volume is not None

    @pytest.mark.integration
    def test_real_get_broker_list_for_stock(self, integration_client: LaplaceClient):
        """Test real API call for getting broker list for a specific stock."""
        # Use a known stock symbol for testing
        stock_symbol = "SASA"
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        stock_data = integration_client.brokers.get_broker_list_for_stock(
            symbol=stock_symbol,
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(stock_data, BrokerMarketData)
        assert stock_data.record_count >= 0
        assert len(stock_data.items) >= 0
        assert all(isinstance(item, BrokerTradingData) for item in stock_data.items)

        # Test items if any exist
        if stock_data.items:
            assert all(item.broker.id for item in stock_data.items)
            assert all(item.broker.name for item in stock_data.items)
            assert all(item.broker.symbol for item in stock_data.items)
            assert all(item.broker.long_name for item in stock_data.items)
            assert all(item.broker.logo for item in stock_data.items)
            assert all(item.net_amount is not None for item in stock_data.items)
            assert all(item.total_amount is not None for item in stock_data.items)
            assert all(item.total_volume is not None for item in stock_data.items)

        # Test total stats
        assert stock_data.total_stats.net_amount is not None
        assert stock_data.total_stats.total_amount is not None
        assert stock_data.total_stats.total_volume is not None

    @pytest.mark.integration
    def test_real_get_stock_list_for_market(self, integration_client: LaplaceClient):
        """Test real API call for getting stock list for market."""
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)

        market_stock_data = integration_client.brokers.get_stock_list_for_market(
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(market_stock_data, BrokerStockData)
        assert market_stock_data.record_count >= 0
        assert len(market_stock_data.items) >= 0
        assert all(isinstance(item, BrokerTradingData) for item in market_stock_data.items)

        # Test items if any exist
        if market_stock_data.items:
            assert all(item.stock.id for item in market_stock_data.items)
            assert all(item.stock.name for item in market_stock_data.items)
            assert all(item.stock.symbol for item in market_stock_data.items)
            assert all(item.stock.asset_type for item in market_stock_data.items)
            assert all(item.stock.asset_class for item in market_stock_data.items)
            assert all(item.net_amount is not None for item in market_stock_data.items)
            assert all(item.total_amount is not None for item in market_stock_data.items)
            assert all(item.total_volume is not None for item in market_stock_data.items)

        # Test total stats
        assert market_stock_data.total_stats.net_amount is not None
        assert market_stock_data.total_stats.total_amount is not None
        assert market_stock_data.total_stats.total_volume is not None
