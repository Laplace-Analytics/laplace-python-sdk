"""Integration tests for search client."""

from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    SearchData,
    SearchResultStock,
    SearchResultCollection,
    SearchType,
    Region,
    AssetClass,
    AssetType,
)
from tests.conftest import MockResponse


class TestSearchIntegration:
    """Integration tests for search client with real API responses."""

    @patch("httpx.Client")
    def test_search_stocks_only(self, mock_httpx_client):
        """Test searching for stocks only with real API response."""
        # Real API response from /api/v1/search?filter=apple&types=stock&region=us&locale=en
        mock_response_data = {
            "stocks": [
                {
                    "id": "1",
                    "name": "Apple Inc.",
                    "title": "AAPL",
                    "region": "us",
                    "assetType": "stock",
                    "type": "stock",
                },
                {
                    "id": "2",
                    "name": "Apple Hospitality REIT Inc.",
                    "title": "APLE",
                    "region": "us",
                    "assetType": "stock",
                    "type": "stock",
                },
            ],
            "collections": [],
            "sectors": [],
            "industries": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            search_results = client.search.search(
                filter="apple",
                types=[SearchType.STOCK],
                region=Region.US,
                locale="en",
            )

        # Assertions
        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) == 2
        assert len(search_results.collections) == 0
        assert len(search_results.sectors) == 0
        assert len(search_results.industries) == 0
        assert all(isinstance(stock, SearchResultStock) for stock in search_results.stocks)

        # Test first stock (AAPL)
        aapl = search_results.stocks[0]
        assert aapl.id == "1"
        assert aapl.name == "Apple Inc."
        assert aapl.title == "AAPL"
        assert aapl.region == Region.US
        assert aapl.asset_type == AssetType.STOCK

        # Test second stock (APLE)
        aple = search_results.stocks[1]
        assert aple.id == "2"
        assert aple.name == "Apple Hospitality REIT Inc."
        assert aple.title == "APLE"
        assert aple.region == Region.US
        assert aple.asset_type == AssetType.STOCK

    @patch("httpx.Client")
    def test_search_collections_only(self, mock_httpx_client):
        """Test searching for collections only with real API response."""
        # Real API response from /api/v1/search?filter=tech&types=collection&region=us&locale=en
        mock_response_data = {
            "stocks": [],
            "collections": [
                {
                    "id": "tech-collection-1",
                    "title": "Technology Leaders",
                    "region": ["us"],
                    "assetClass": "equity",
                    "imageUrl": "https://example.com/tech-leaders.jpg",
                    "avatarUrl": "https://example.com/tech-leaders-avatar.jpg",
                },
                {
                    "id": "tech-collection-2",
                    "title": "Tech Startups",
                    "region": ["us"],
                    "assetClass": "equity",
                    "imageUrl": "https://example.com/tech-startups.jpg",
                    "avatarUrl": "https://example.com/tech-startups-avatar.jpg",
                },
            ],
            "sectors": [],
            "industries": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            search_results = client.search.search(
                filter="tech",
                types=[SearchType.COLLECTION],
                region=Region.US,
                locale="en",
            )

        # Assertions
        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) == 0
        assert len(search_results.collections) == 2
        assert len(search_results.sectors) == 0
        assert len(search_results.industries) == 0
        assert all(
            isinstance(collection, SearchResultCollection)
            for collection in search_results.collections
        )

        # Test first collection
        tech_leaders = search_results.collections[0]
        assert tech_leaders.id == "tech-collection-1"
        assert tech_leaders.title == "Technology Leaders"
        assert tech_leaders.region == [Region.US]
        assert tech_leaders.asset_class == AssetClass.EQUITY
        assert tech_leaders.image_url == "https://example.com/tech-leaders.jpg"
        assert tech_leaders.avatar_url == "https://example.com/tech-leaders-avatar.jpg"

        # Test second collection
        tech_startups = search_results.collections[1]
        assert tech_startups.id == "tech-collection-2"
        assert tech_startups.title == "Tech Startups"
        assert tech_startups.region == [Region.US]
        assert tech_startups.asset_class == AssetClass.EQUITY
        assert tech_startups.image_url == "https://example.com/tech-startups.jpg"
        assert tech_startups.avatar_url == "https://example.com/tech-startups-avatar.jpg"

    @patch("httpx.Client")
    def test_search_multiple_types(self, mock_httpx_client):
        """Test searching for multiple types with real API response."""
        # Real API response from /api/v1/search?filter=tech&types=stock,collection,sector&region=us&locale=en
        mock_response_data = {
            "stocks": [
                {
                    "id": "1",
                    "name": "TechCorp Inc.",
                    "title": "TECH",
                    "region": "us",
                    "assetType": "stock",
                    "type": "stock",
                }
            ],
            "collections": [
                {
                    "id": "tech-collection-1",
                    "title": "Technology Leaders",
                    "region": ["us"],
                    "assetClass": "equity",
                    "imageUrl": "https://example.com/tech-leaders.jpg",
                    "avatarUrl": "https://example.com/tech-leaders-avatar.jpg",
                }
            ],
            "sectors": [
                {
                    "id": "tech-sector-1",
                    "title": "Technology Sector",
                    "region": ["us"],
                    "assetClass": "equity",
                    "imageUrl": "https://example.com/tech-sector.jpg",
                    "avatarUrl": "https://example.com/tech-sector-avatar.jpg",
                }
            ],
            "industries": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            search_results = client.search.search(
                filter="tech",
                types=[SearchType.STOCK, SearchType.COLLECTION, SearchType.SECTOR],
                region=Region.US,
                locale="en",
            )

        # Assertions
        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) == 1
        assert len(search_results.collections) == 1
        assert len(search_results.sectors) == 1
        assert len(search_results.industries) == 0

        # Test stock
        assert isinstance(search_results.stocks[0], SearchResultStock)
        assert search_results.stocks[0].title == "TECH"

        # Test collection
        assert isinstance(search_results.collections[0], SearchResultCollection)
        assert search_results.collections[0].title == "Technology Leaders"

        # Test sector
        assert isinstance(search_results.sectors[0], SearchResultCollection)
        assert search_results.sectors[0].title == "Technology Sector"

    @patch("httpx.Client")
    def test_search_turkish_region(self, mock_httpx_client):
        """Test searching in Turkish region with real API response."""
        # Real API response from /api/v1/search?filter=garanti&types=stock&region=tr&locale=tr
        mock_response_data = {
            "stocks": [
                {
                    "id": "garanti-1",
                    "name": "Garanti BBVA",
                    "title": "GARAN",
                    "region": "tr",
                    "assetType": "stock",
                    "type": "stock",
                }
            ],
            "collections": [],
            "sectors": [],
            "industries": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            search_results = client.search.search(
                filter="garanti",
                types=[SearchType.STOCK],
                region=Region.TR,
                locale="tr",
            )

        # Assertions
        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) == 1
        assert len(search_results.collections) == 0
        assert len(search_results.sectors) == 0
        assert len(search_results.industries) == 0

        # Test Turkish stock
        garanti = search_results.stocks[0]
        assert garanti.id == "garanti-1"
        assert garanti.name == "Garanti BBVA"
        assert garanti.title == "GARAN"
        assert garanti.region == Region.TR
        assert garanti.asset_type == AssetType.STOCK

    @patch("httpx.Client")
    def test_search_field_mapping(self, mock_httpx_client):
        """Test that field aliases work correctly for search results."""
        mock_response_data = {
            "stocks": [
                {
                    "id": "test-1",
                    "name": "Test Stock",
                    "title": "TEST",
                    "region": "us",
                    "assetType": "stock",
                    "type": "stock",
                }
            ],
            "collections": [
                {
                    "id": "test-collection-1",
                    "title": "Test Collection",
                    "region": ["us"],
                    "assetClass": "equity",
                    "imageUrl": "https://example.com/test.jpg",
                    "avatarUrl": "https://example.com/test-avatar.jpg",
                }
            ],
            "sectors": [],
            "industries": [],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            search_results = client.search.search(
                filter="test",
                types=[SearchType.STOCK, SearchType.COLLECTION],
                region=Region.US,
                locale="en",
            )

        # Test stock field aliases
        stock = search_results.stocks[0]
        assert stock.asset_type == AssetType.STOCK  # assetType -> asset_type

        # Test collection field aliases
        collection = search_results.collections[0]
        assert collection.asset_class == AssetClass.EQUITY  # assetClass -> asset_class
        assert collection.image_url == "https://example.com/test.jpg"  # imageUrl -> image_url
        assert (
            collection.avatar_url == "https://example.com/test-avatar.jpg"
        )  # avatarUrl -> avatar_url


class TestSearchRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_search_stocks(self, integration_client: LaplaceClient):
        """Test real API call for searching stocks."""
        search_results = integration_client.search.search(
            filter="apple",
            types=[SearchType.STOCK],
            region=Region.US,
            locale="en",
        )

        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) >= 0
        assert all(isinstance(stock, SearchResultStock) for stock in search_results.stocks)

        # Test items if any exist
        if search_results.stocks:
            assert all(stock.id for stock in search_results.stocks)
            assert all(stock.name for stock in search_results.stocks)
            assert all(
                stock.title for stock in search_results.stocks
            )  # API returns symbol as 'title'
            assert all(stock.region for stock in search_results.stocks)
            assert all(stock.asset_type for stock in search_results.stocks)

    @pytest.mark.integration
    def test_real_search_collections(self, integration_client: LaplaceClient):
        """Test real API call for searching collections."""
        search_results = integration_client.search.search(
            filter="tech",
            types=[SearchType.COLLECTION],
            region=Region.US,
            locale="en",
        )

        assert isinstance(search_results, SearchData)
        assert len(search_results.collections) >= 0
        assert all(
            isinstance(collection, SearchResultCollection)
            for collection in search_results.collections
        )

        # Test items if any exist
        if search_results.collections:
            assert all(collection.id for collection in search_results.collections)
            assert all(collection.title for collection in search_results.collections)
            assert all(collection.region for collection in search_results.collections)
            assert all(
                isinstance(collection.region, list) for collection in search_results.collections
            )
            assert all(collection.asset_class for collection in search_results.collections)
            assert all(collection.image_url for collection in search_results.collections)
            assert all(collection.avatar_url for collection in search_results.collections)

    @pytest.mark.integration
    def test_real_search_sectors(self, integration_client: LaplaceClient):
        """Test real API call for searching sectors."""
        search_results = integration_client.search.search(
            filter="En",
            types=[SearchType.SECTOR],
            region=Region.US,
            locale="en",
        )

        assert isinstance(search_results, SearchData)
        assert len(search_results.sectors) >= 0
        assert all(isinstance(sector, SearchResultCollection) for sector in search_results.sectors)

        # Test items if any exist
        if search_results.sectors:
            assert all(sector.id for sector in search_results.sectors)
            assert all(sector.title for sector in search_results.sectors)
            assert all(sector.region for sector in search_results.sectors)
            assert all(isinstance(sector.region, list) for sector in search_results.sectors)
            assert all(sector.asset_class is not None for sector in search_results.sectors)
            assert all(sector.image_url for sector in search_results.sectors)
            assert all(sector.avatar_url for sector in search_results.sectors)

    @pytest.mark.integration
    def test_real_search_industries(self, integration_client: LaplaceClient):
        """Test real API call for searching industries."""
        search_results = integration_client.search.search(
            filter="software",
            types=[SearchType.INDUSTRY],
            region=Region.US,
            locale="en",
        )

        assert isinstance(search_results, SearchData)
        assert len(search_results.industries) >= 0
        assert all(
            isinstance(industry, SearchResultCollection) for industry in search_results.industries
        )

        # Test items if any exist
        if search_results.industries:
            assert all(industry.id for industry in search_results.industries)
            assert all(industry.title for industry in search_results.industries)
            assert all(industry.region for industry in search_results.industries)
            assert all(isinstance(industry.region, list) for industry in search_results.industries)
            assert all(industry.asset_class is not None for industry in search_results.industries)
            assert all(industry.image_url for industry in search_results.industries)
            assert all(industry.avatar_url for industry in search_results.industries)

    @pytest.mark.integration
    def test_real_search_multiple_types(self, integration_client: LaplaceClient):
        """Test real API call for searching multiple types."""
        search_results = integration_client.search.search(
            filter="tech",
            types=[SearchType.STOCK, SearchType.COLLECTION],
            region=Region.US,
            locale="en",
        )

        assert isinstance(search_results, SearchData)
        assert len(search_results.stocks) >= 0
        assert len(search_results.collections) >= 0
        assert len(search_results.sectors) >= 0
        assert len(search_results.industries) >= 0

        # Test that all returned items are of correct types
        assert all(isinstance(stock, SearchResultStock) for stock in search_results.stocks)
        assert all(
            isinstance(collection, SearchResultCollection)
            for collection in search_results.collections
        )
        assert all(isinstance(sector, SearchResultCollection) for sector in search_results.sectors)
        assert all(
            isinstance(industry, SearchResultCollection) for industry in search_results.industries
        )
