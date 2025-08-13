"""Integration tests for collections client."""

from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import Collection, CollectionDetail, CollectionStock, Region
from tests.conftest import MockResponse


class TestCollectionsIntegration:
    """Integration tests for collections client with real API responses."""

    @patch("httpx.Client")
    def test_get_collections(self, mock_httpx_client):
        """Test getting collections with real API response."""
        # Real API response from /api/v1/collection?region=tr&locale=en
        mock_response_data = [
            {
                "id": "620f455a0187ade00bb0d55f",
                "title": "Large Cap",
                "region": ["tr"],
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyukler_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyukler_avatar.webp",
                "numStocks": 10,
                "assetClass": "equity",
            },
            {
                "id": "64fee022215898698650bfc9",
                "title": "Clothing",
                "region": ["tr"],
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/mens-clothing-stores.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/mens-clothing-stores_avatar.webp",
                "numStocks": 5,
                "assetClass": "equity",
            },
            {
                "id": "622df02a38290f0011081ab9",
                "title": "Largest Cryptos",
                "region": ["tr"],
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyuk-kriptolar_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyuk-kriptolar_avatar.webp",
                "numStocks": 11,
                "assetClass": "crypto",
            },
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            collections = client.collections.get_collections(region=Region.TR, locale="en")

        # Assertions
        assert len(collections) == 3
        assert isinstance(collections[0], Collection)

        # Test Large Cap collection
        large_cap = collections[0]
        assert large_cap.id == "620f455a0187ade00bb0d55f"
        assert large_cap.title == "Large Cap"
        assert large_cap.region == ["tr"]
        assert large_cap.num_stocks == 10
        assert large_cap.asset_class == "equity"
        assert "en-buyukler_original.webp" in large_cap.image_url
        assert "en-buyukler_avatar.webp" in large_cap.avatar_url

        # Test Clothing collection
        clothing = collections[1]
        assert clothing.id == "64fee022215898698650bfc9"
        assert clothing.title == "Clothing"
        assert clothing.num_stocks == 5
        assert clothing.asset_class == "equity"

        # Test Crypto collection
        crypto = collections[2]
        assert crypto.id == "622df02a38290f0011081ab9"
        assert crypto.title == "Largest Cryptos"
        assert crypto.num_stocks == 11
        assert crypto.asset_class == "crypto"

    @patch("httpx.Client")
    def test_get_collection_detail(self, mock_httpx_client):
        """Test getting collection detail with real API response."""
        # Real API response from /api/v1/collection/620f455a0187ade00bb0d55f?locale=en&region=tr
        mock_response_data = {
            "id": "620f455a0187ade00bb0d55f",
            "title": "Large Cap",
            "region": ["tr"],
            "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyukler_original.webp",
            "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/en-buyukler_avatar.webp",
            "numStocks": 10,
            "assetClass": "equity",
            "stocks": [
                {
                    "id": "61dd0d670ec2114146342fa5",
                    "assetType": "stock",
                    "name": "SASA Polyester",
                    "symbol": "SASA",
                    "sectorId": "65533e047844ee7afe9941c0",
                    "industryId": "65533e441fa5c7b58afa097a",
                    "updatedDate": "2022-01-11T04:53:59.57Z",
                    "active": True,
                },
                {
                    "id": "61dd0d7a0ec2114146343014",
                    "assetType": "stock",
                    "name": "Koç Holding",
                    "symbol": "KCHOL",
                    "sectorId": "65533e047844ee7afe9941be",
                    "industryId": "65533e441fa5c7b58afa0956",
                    "updatedDate": "2022-01-11T04:54:18.718Z",
                    "active": True,
                },
                {
                    "id": "61dd0d4b0ec2114146342f6a",
                    "assetType": "stock",
                    "name": "Garanti Bankası",
                    "symbol": "GARAN",
                    "sectorId": "65533e047844ee7afe9941bc",
                    "industryId": "65533e441fa5c7b58afa0953",
                    "updatedDate": "2025-04-01T00:00:00.533Z",
                    "active": True,
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            collection_detail = client.collections.get_collection_detail(
                collection_id="620f455a0187ade00bb0d55f", region=Region.TR, locale="en"
            )

        # Assertions
        assert isinstance(collection_detail, CollectionDetail)
        assert collection_detail.id == "620f455a0187ade00bb0d55f"
        assert collection_detail.title == "Large Cap"
        assert collection_detail.region == ["tr"]
        assert collection_detail.num_stocks == 10
        assert collection_detail.asset_class == "equity"
        assert "en-buyukler_original.webp" in collection_detail.image_url
        assert "en-buyukler_avatar.webp" in collection_detail.avatar_url

        # Test stocks within collection
        assert len(collection_detail.stocks) == 3
        assert all(isinstance(stock, CollectionStock) for stock in collection_detail.stocks)

        # Test first stock (SASA)
        sasa = collection_detail.stocks[0]
        assert sasa.id == "61dd0d670ec2114146342fa5"
        assert sasa.name == "SASA Polyester"
        assert sasa.symbol == "SASA"
        assert sasa.asset_type == "stock"
        assert sasa.sector_id == "65533e047844ee7afe9941c0"
        assert sasa.industry_id == "65533e441fa5c7b58afa097a"

        # Test second stock (Koç Holding)
        koc = collection_detail.stocks[1]
        assert koc.id == "61dd0d7a0ec2114146343014"
        assert koc.name == "Koç Holding"
        assert koc.symbol == "KCHOL"
        assert koc.asset_type == "stock"

        # Test third stock (Garanti Bank)
        garan = collection_detail.stocks[2]
        assert garan.id == "61dd0d4b0ec2114146342f6a"
        assert garan.name == "Garanti Bankası"
        assert garan.symbol == "GARAN"
        assert garan.asset_type == "stock"

    @patch("httpx.Client")
    def test_collections_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for collections."""
        mock_response_data = [
            {
                "id": "test-id",
                "title": "Test Collection",
                "region": ["us"],
                "imageUrl": "https://example.com/image.jpg",
                "avatarUrl": "https://example.com/avatar.jpg",
                "numStocks": 5,
                "assetClass": "equity",
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            collections = client.collections.get_collections(region=Region.US, locale="en")

        collection = collections[0]

        # Test field aliases work
        assert collection.image_url == "https://example.com/image.jpg"  # imageUrl -> image_url
        assert collection.avatar_url == "https://example.com/avatar.jpg"  # avatarUrl -> avatar_url
        assert collection.num_stocks == 5  # numStocks -> num_stocks
        assert collection.asset_class == "equity"  # assetClass -> asset_class

    @patch("httpx.Client")
    def test_collection_stock_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for collection stocks."""
        mock_response_data = {
            "id": "test-collection-id",
            "title": "Test Collection",
            "region": ["tr"],
            "imageUrl": "https://example.com/image.jpg",
            "avatarUrl": "https://example.com/avatar.jpg",
            "numStocks": 1,
            "assetClass": "equity",
            "stocks": [
                {
                    "id": "test-stock-id",
                    "name": "Test Stock",
                    "symbol": "TEST",
                    "sectorId": "test-sector-id",
                    "assetType": "stock",
                    "industryId": "test-industry-id",
                }
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            collection_detail = client.collections.get_collection_detail(
                collection_id="test-collection-id", region=Region.TR, locale="en"
            )

        stock = collection_detail.stocks[0]

        # Test field aliases work for stocks
        assert stock.sector_id == "test-sector-id"  # sectorId -> sector_id
        assert stock.asset_type == "stock"  # assetType -> asset_type
        assert stock.industry_id == "test-industry-id"  # industryId -> industry_id


class TestCollectionsRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_collections(self, integration_client: LaplaceClient):
        """Test real API call for getting collections."""
        collections = integration_client.collections.get_collections(region=Region.TR, locale="en")

        assert len(collections) > 0
        assert all(isinstance(collection, Collection) for collection in collections)
        assert all(collection.id for collection in collections)
        assert all(collection.title for collection in collections)
        assert all(collection.region for collection in collections)
        assert all(collection.num_stocks >= 0 for collection in collections)
        assert all(collection.asset_class for collection in collections)

    @pytest.mark.integration
    def test_real_get_collection_detail(self, integration_client: LaplaceClient):
        """Test real API call for getting collection detail."""
        # First get a collection to get a valid ID
        collections = integration_client.collections.get_collections(region=Region.TR, locale="en")
        assert len(collections) > 0

        collection_id = collections[0].id

        # Now get the detail
        collection_detail = integration_client.collections.get_collection_detail(
            collection_id=collection_id, region=Region.TR, locale="en"
        )

        assert isinstance(collection_detail, CollectionDetail)
        assert collection_detail.id == collection_id
        assert collection_detail.title
        assert collection_detail.region
        assert collection_detail.num_stocks >= 0
        assert collection_detail.asset_class
        assert isinstance(collection_detail.stocks, list)

        # Test stocks if any exist
        if collection_detail.stocks:
            assert all(isinstance(stock, CollectionStock) for stock in collection_detail.stocks)
            assert all(stock.id for stock in collection_detail.stocks)
            assert all(stock.name for stock in collection_detail.stocks)
            assert all(stock.symbol for stock in collection_detail.stocks)
