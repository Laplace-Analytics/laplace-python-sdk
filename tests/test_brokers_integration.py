"""Integration tests for brokers client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    Broker,
    BrokerItem,
    BrokerList,
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
            "items": [
                {
                    "id": 1,
                    "logo": "https://finfree-storage.s3.eu-central-1.amazonaws.com/brokers/BIDZY.svg",
                    "name": "DENIZ YATIRIM",
                    "symbol": "BIDZY",
                    "longName": "DENIZ YATIRIM MENKUL KIYMETLER A.S.",
                    "supportedAssetClasses": [
                        "equity"
                    ]
                },
            ],
            "recordCount": 239
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.brokers.get_brokers(
                region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
            )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 239
        assert len(response.items) == 1
        assert all(isinstance(broker, Broker) for broker in response.items)

        item = response.items[0]
        assert item.id == 1
        assert item.name == "DENIZ YATIRIM"
        assert item.symbol == "BIDZY"
        assert item.long_name == "DENIZ YATIRIM MENKUL KIYMETLER A.S."
        assert item.logo == "https://finfree-storage.s3.eu-central-1.amazonaws.com/brokers/BIDZY.svg"
        assert "equity" in item.supported_asset_classes

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

        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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
        assert isinstance(broker_data, BrokerList)
        assert len(broker_data.items) == 2
        assert broker_data.record_count == 2
        assert all(isinstance(item, BrokerItem) for item in broker_data.items)

        # Test first stock (SASA)
        sasa = broker_data.items[0]
        assert sasa.stock.id == "61dd0d670ec2114146342fa5"
        assert sasa.stock.name == "SASA Polyester"
        assert sasa.stock.symbol == "SASA"
        assert sasa.stock.asset_type == "stock"
        assert sasa.stock.asset_class == "equity"
        assert sasa.net_amount == 500000.00
        assert sasa.total_amount == 2000000.00
        assert sasa.total_volume == 40000
        assert sasa.total_buy_amount == 1250000.00
        assert sasa.total_sell_amount == 750000.00
        assert sasa.total_buy_volume == 20000
        assert sasa.total_sell_volume == 20000

        # Test second stock (KCHOL)
        kchol = broker_data.items[1]
        assert kchol.stock.id == "61dd0d7a0ec2114146343014"
        assert kchol.stock.name == "Koç Holding"
        assert kchol.stock.symbol == "KCHOL"
        assert kchol.stock.asset_type == "stock"
        assert kchol.stock.asset_class == "equity"
        assert kchol.net_amount == 300000.00
        assert kchol.total_amount == 1500000.00
        assert kchol.total_volume == 30000
        assert kchol.total_buy_amount == 900000.00
        assert kchol.total_sell_amount == 600000.00
        assert kchol.total_buy_volume == 15000
        assert kchol.total_sell_volume == 15000

        # Test total stats
        total_stats = broker_data.total_stats

        assert total_stats.net_amount == 800000.00
        assert total_stats.total_amount == 3500000.00
        assert total_stats.total_volume == 70000
        assert total_stats.total_buy_amount == 2150000.00
        assert total_stats.total_sell_amount == 1350000.00
        assert total_stats.total_buy_volume == 35000
        assert total_stats.total_sell_volume == 35000

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
                }
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

        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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
        assert isinstance(market_data, BrokerList)
        assert len(market_data.items) == 1
        assert market_data.record_count == 2
        assert all(isinstance(item, BrokerItem) for item in market_data.items)

        # Test first broker (BIMLB)
        bimlb = market_data.items[0]
        assert bimlb.broker.id == 1
        assert bimlb.broker.name == "BIMLB"
        assert bimlb.broker.symbol == "BIMLB"
        assert bimlb.broker.long_name == "BIM Yatırım Menkul Değerler A.Ş."
        assert bimlb.broker.logo == "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/bimlb.png"
        assert bimlb.net_amount == 2500000.00
        assert bimlb.total_amount == 10000000.00
        assert bimlb.total_volume == 200000
        assert bimlb.total_buy_amount == 6250000.00
        assert bimlb.total_sell_amount == 3750000.00
        assert bimlb.total_buy_volume == 100000
        assert bimlb.total_sell_volume == 100000

        # Test total stats
        total_stats = market_data.total_stats

        assert total_stats.net_amount == 4000000.00
        assert total_stats.total_amount == 17500000.00
        assert total_stats.total_volume == 350000
        assert total_stats.total_buy_amount == 10750000.00
        assert total_stats.total_sell_amount == 6750000.00
        assert total_stats.total_buy_volume == 175000
        assert total_stats.total_sell_volume == 175000

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
                    "averageCost": 2.91,
                    "netAmount": 500000.00,
                    "totalAmount": 2000000.00,
                    "totalVolume": 40000,
                    "totalBuyAmount": 1250000.00,
                    "totalBuyVolume": 20000,
                    "totalSellAmount": 750000.00,
                    "totalSellVolume": 20000,
                }
            ],
            "totalStats": {
                "averageCost": 2.91,
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

        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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
        assert isinstance(broker_data, BrokerList)
        assert len(broker_data.items) == 1
        assert broker_data.record_count == 2
        assert all(isinstance(item, BrokerItem) for item in broker_data.items)

        # Test first broker (BIMLB)
        bimlb = broker_data.items[0]
        assert bimlb.broker.id == 1
        assert bimlb.broker.name == "BIMLB"
        assert bimlb.broker.symbol == "BIMLB"
        assert bimlb.broker.logo == "https://finfree-storage.s3.eu-central-1.amazonaws.com/broker-logos/bimlb.png"
        assert bimlb.broker.long_name == "BIM Yatırım Menkul Değerler A.Ş."
        assert bimlb.net_amount == 500000.00
        assert bimlb.total_amount == 2000000.00
        assert bimlb.total_volume == 40000
        assert bimlb.average_cost == 2.91
        assert bimlb.total_buy_amount == 1250000.00
        assert bimlb.total_buy_volume == 20000
        assert bimlb.total_sell_amount == 750000.00
        assert bimlb.total_sell_volume == 20000

        # Test total stats
        total_stats = broker_data.total_stats
        assert total_stats.net_amount == 800000.00
        assert total_stats.total_amount == 3500000.00
        assert total_stats.total_volume == 70000
        assert total_stats.average_cost == 2.91
        assert total_stats.total_buy_amount == 2150000.00
        assert total_stats.total_buy_volume == 35000
        assert total_stats.total_sell_amount == 1350000.00
        assert total_stats.total_sell_volume == 35000

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
                    "averageCost": 2.91,
                    "netAmount": 1000000.00,
                    "totalAmount": 5000000.00,
                    "totalVolume": 100000,
                    "totalBuyAmount": 3000000.00,
                    "totalBuyVolume": 50000,
                    "totalSellAmount": 2000000.00,
                    "totalSellVolume": 50000,
                }
            ],
            "totalStats": {
                "averageCost": 2.91,
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

        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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
        assert isinstance(market_stock_data, BrokerList)
        assert len(market_stock_data.items) == 1
        assert market_stock_data.record_count == 2

        # Test first stock (SASA)
        sasa = market_stock_data.items[0]
        assert sasa.stock.name == "SASA Polyester"
        assert sasa.stock.symbol == "SASA"
        assert sasa.stock.id == "61dd0d670ec2114146342fa5"
        assert sasa.stock.asset_type == "stock"
        assert sasa.stock.asset_class == "equity"

        assert sasa.net_amount == 1000000.00
        assert sasa.total_amount == 5000000.00
        assert sasa.total_volume == 100000
        assert sasa.average_cost == 2.91
        assert sasa.total_buy_amount == 3000000.00
        assert sasa.total_buy_volume == 50000
        assert sasa.total_sell_amount == 2000000.00
        assert sasa.total_sell_volume == 50000

        # Test total stats
        total_stats = market_stock_data.total_stats
        assert total_stats.net_amount == 1750000.00
        assert total_stats.total_amount == 8750000.00
        assert total_stats.total_volume == 175000
        assert total_stats.average_cost == 2.91
        assert total_stats.total_buy_amount == 5250000.00
        assert total_stats.total_buy_volume == 87500
        assert total_stats.total_sell_amount == 3500000.00
        assert total_stats.total_sell_volume == 87500

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
                from_date=datetime(2025, 6, 1),
                to_date=datetime(2025, 6, 30),
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
        assert isinstance(response.record_count, int)
        assert response.record_count >= 0
        assert isinstance(response.items, list)

        if response.items:
            broker = response.items[0]

            assert isinstance(broker, Broker)
            assert broker.id
            assert broker.name
            assert broker.symbol
            assert broker.long_name
            assert isinstance(broker.logo, str) or broker.logo is None

    @pytest.mark.integration
    def test_real_get_stock_list_for_broker(self, integration_client: LaplaceClient):
        """Test real API call for getting stock list for a specific broker."""
        # First get all brokers to get a valid symbol
        response = integration_client.brokers.get_brokers(
            region=Region.TR, page=0, size=PaginationPageSize.PAGE_SIZE_10
        )
        assert len(response.items) > 0

        broker_symbol = response.items[0].symbol
        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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

        assert isinstance(broker_data, BrokerList)
        assert broker_data.record_count >= 0
        assert len(broker_data.items) >= 0
        assert all(isinstance(item, BrokerItem) for item in broker_data.items)

        if broker_data.items:
            item = broker_data.items[0]
            assert item.stock.id
            assert item.stock.name
            assert item.stock.symbol
            assert item.stock.asset_type
            assert item.stock.asset_class

            assert isinstance(item.net_amount, (int, float))
            assert isinstance(item.total_amount, (int, float))
            assert isinstance(item.total_volume, (int, float))
            assert isinstance(item.total_buy_amount, (int, float))
            assert isinstance(item.total_sell_amount, (int, float))
            assert isinstance(item.total_buy_volume, (int, float))
            assert isinstance(item.total_sell_volume, (int, float))

        ts = broker_data.total_stats
        assert isinstance(ts.net_amount, (int, float))
        assert isinstance(ts.total_amount, (int, float))
        assert isinstance(ts.total_volume, (int, float))
        assert isinstance(ts.total_buy_amount, (int, float))
        assert isinstance(ts.total_sell_amount, (int, float))
        assert isinstance(ts.total_buy_volume, (int, float))
        assert isinstance(ts.total_sell_volume, (int, float))

    @pytest.mark.integration
    def test_real_get_broker_list_for_market(self, integration_client: LaplaceClient):
        """Test real API call for getting broker list for market."""
        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

        market_data = integration_client.brokers.get_broker_list_for_market(
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(market_data, BrokerList)
        assert market_data.record_count >= 0
        assert len(market_data.items) >= 0
        assert all(isinstance(item, BrokerItem) for item in market_data.items)

        if market_data.items:
            item = market_data.items[0]
            assert item.broker.id
            assert item.broker.name
            assert item.broker.symbol

            assert isinstance(item.net_amount, (int, float))
            assert isinstance(item.total_amount, (int, float))
            assert isinstance(item.total_volume, (int, float))
            assert isinstance(item.total_buy_amount, (int, float))
            assert isinstance(item.total_sell_amount, (int, float))
            assert isinstance(item.total_buy_volume, (int, float))
            assert isinstance(item.total_sell_volume, (int, float))

        ts = market_data.total_stats
        assert isinstance(ts.net_amount, (int, float))
        assert isinstance(ts.total_amount, (int, float))
        assert isinstance(ts.total_volume, (int, float))
        assert isinstance(ts.total_buy_amount, (int, float))
        assert isinstance(ts.total_sell_amount, (int, float))
        assert isinstance(ts.total_buy_volume, (int, float))
        assert isinstance(ts.total_sell_volume, (int, float))


    @pytest.mark.integration
    def test_real_get_broker_list_for_stock(self, integration_client: LaplaceClient):
        """Test real API call for getting broker list for a specific stock."""
        # Use a known stock symbol for testing
        stock_symbol = "SASA"
        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

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

        assert isinstance(stock_data, BrokerList)
        assert stock_data.record_count >= 0
        assert len(stock_data.items) >= 0
        assert all(isinstance(item, BrokerItem) for item in stock_data.items)

        if stock_data.items:
            item = stock_data.items[0]
            assert item.broker.id
            assert item.broker.name
            assert item.broker.symbol
            assert item.broker.long_name
            assert isinstance(item.broker.logo, str) or item.broker.logo is None

            assert isinstance(item.net_amount, (int, float))
            assert isinstance(item.total_amount, (int, float))
            assert isinstance(item.total_volume, (int, float))
            assert isinstance(item.total_buy_amount, (int, float))
            assert isinstance(item.total_sell_amount, (int, float))
            assert isinstance(item.total_buy_volume, (int, float))
            assert isinstance(item.total_sell_volume, (int, float))
            assert isinstance(item.average_cost, (int, float))

        ts = stock_data.total_stats
        assert isinstance(ts.net_amount, (int, float))
        assert isinstance(ts.total_amount, (int, float))
        assert isinstance(ts.total_volume, (int, float))
        assert isinstance(ts.average_cost, (int, float))
        assert isinstance(ts.total_buy_amount, (int, float))
        assert isinstance(ts.total_sell_amount, (int, float))
        assert isinstance(ts.total_buy_volume, (int, float))
        assert isinstance(ts.total_sell_volume, (int, float))



    @pytest.mark.integration
    def test_real_get_stock_list_for_market(self, integration_client: LaplaceClient):
        """Test real API call for getting stock list for market."""
        from_date = datetime(2025, 6, 1)
        to_date = datetime(2025, 6, 30)

        market_stock_data = integration_client.brokers.get_stock_list_for_market(
            region=Region.TR,
            sort_by=BrokerSort.NET_AMOUNT,
            sort_direction=SortDirection.DESC,
            from_date=from_date,
            to_date=to_date,
            page=0,
            size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(market_stock_data, BrokerList)
        assert market_stock_data.record_count >= 0
        assert len(market_stock_data.items) >= 0
        assert all(isinstance(item, BrokerItem) for item in market_stock_data.items)

        if market_stock_data.items:
            item = market_stock_data.items[0]
            assert item.stock.id
            assert item.stock.name
            assert item.stock.symbol
            assert item.stock.asset_type
            assert item.stock.asset_class

            assert isinstance(item.net_amount, (int, float))
            assert isinstance(item.total_amount, (int, float))
            assert isinstance(item.total_volume, (int, float))
            assert isinstance(item.total_buy_amount, (int, float))
            assert isinstance(item.total_sell_amount, (int, float))
            assert isinstance(item.total_buy_volume, (int, float))
            assert isinstance(item.total_sell_volume, (int, float))
            assert isinstance(item.average_cost, (int, float))

        ts = market_stock_data.total_stats
        assert isinstance(ts.net_amount, (int, float))
        assert isinstance(ts.total_amount, (int, float))
        assert isinstance(ts.total_volume, (int, float))
        assert isinstance(ts.average_cost, (int, float))
        assert isinstance(ts.total_buy_amount, (int, float))
        assert isinstance(ts.total_sell_amount, (int, float))
        assert isinstance(ts.total_buy_volume, (int, float))
        assert isinstance(ts.total_sell_volume, (int, float))

