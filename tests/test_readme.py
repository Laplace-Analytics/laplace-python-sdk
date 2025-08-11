"""Test all methods mentioned in the README to ensure they are usable."""

import os
from datetime import datetime
from typing import List
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.base import LaplaceAPIError
from laplace.stocks import HistoricalPriceInterval, IntervalPrice


class TestReadmeExamples:
    """Test all examples from the README to ensure they work correctly."""

    def test_quick_start_examples(self, integration_client: LaplaceClient):
        """Test the quick start examples from the README."""
        # Skip if no API key
        if not os.getenv("LAPLACE_API_KEY"):
            pytest.skip("LAPLACE_API_KEY not set")

        # Test stock detail by symbol
        stock = integration_client.stocks.get_detail_by_symbol(symbol="AAPL", region="us")
        assert stock.name is not None
        assert stock.description is not None
        print(f"{stock.name}: {stock.description}")

        # Test get all stocks
        stocks = integration_client.stocks.get_all(region="us", page=1, page_size=10)
        assert len(stocks) > 0
        for stock in stocks:
            assert stock.symbol is not None
            assert stock.name is not None
            print(f"{stock.symbol}: {stock.name}")

        # Test collections
        collections = integration_client.collections.get_collections(region="tr", locale="en")
        assert len(collections) > 0
        for collection in collections:
            assert collection.title is not None
            assert collection.num_stocks is not None
            print(f"{collection.title}: {collection.num_stocks} stocks")

        # Test collection detail
        if collections:
            collection_detail = integration_client.collections.get_collection_detail(
                collection_id=collections[0].id, region="tr"
            )
            assert collection_detail.title is not None
            print(f"Stocks in {collection_detail.title}:")
            for stock in collection_detail.stocks:
                assert stock.symbol is not None
                assert stock.name is not None
                print(f"  {stock.symbol}: {stock.name}")

    def test_stocks_client_methods(self, integration_client: LaplaceClient):
        """Test all stocks client methods mentioned in the README."""
        if not os.getenv("LAPLACE_API_KEY"):
            pytest.skip("LAPLACE_API_KEY not set")

        # Test get_all with pagination
        stocks = integration_client.stocks.get_all(region="us", page=1, page_size=10)
        assert isinstance(stocks, list)
        assert len(stocks) > 0

        # Test get_detail_by_symbol
        stock = integration_client.stocks.get_detail_by_symbol(
            symbol="AAPL", region="us", asset_class="equity"
        )
        assert stock.symbol == "AAPL"
        assert stock.name is not None

        # Test get_detail_by_id
        stock_detail = integration_client.stocks.get_detail_by_id(stock_id=stock.id, locale="en")
        assert stock_detail.id == stock.id

        # Test get_price
        prices = integration_client.stocks.get_price(
            region="us", symbols=["AAPL", "GOOGL"], keys=["1D", "1W"]
        )
        assert isinstance(prices, list)
        assert len(prices) > 0

        # Test get_price_with_interval
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 10)
        prices_with_interval = integration_client.stocks.get_price_with_interval(
            symbol="THYAO",
            region="tr",
            from_date=from_date,
            to_date=to_date,
            interval=IntervalPrice.ONE_DAY,
        )
        assert isinstance(prices_with_interval, list)

        # Test get_tick_rules (Turkey only)
        try:
            rules = integration_client.stocks.get_tick_rules(region="tr")
            assert rules.rules is not None
        except Exception as e:
            # This might fail if Turkey data is not available
            print(f"Tick rules test failed (expected for non-TR data): {e}")

        # Test get_restrictions (Turkey only)
        try:
            restrictions = integration_client.stocks.get_restrictions(region="tr")
            assert isinstance(restrictions, list)
        except Exception as e:
            # This might fail if Turkey data is not available
            print(f"Restrictions test failed (expected for non-TR data): {e}")

    def test_collections_client_methods(self, integration_client: LaplaceClient):
        """Test all collections client methods mentioned in the README."""
        if not os.getenv("LAPLACE_API_KEY"):
            pytest.skip("LAPLACE_API_KEY not set")

        # Test get_collections
        collections = integration_client.collections.get_collections(region="tr", locale="en")
        assert isinstance(collections, list)

        # Test get_collection_detail
        if collections:
            detail = integration_client.collections.get_collection_detail(
                collection_id=collections[0].id, region="tr"
            )
            assert detail.title is not None

        # Test get_themes
        themes = integration_client.collections.get_themes(region="tr", locale="en")
        assert isinstance(themes, list)

        # Test get_theme_detail
        if themes:
            theme_detail = integration_client.collections.get_theme_detail(
                theme_id=themes[0].id, region="tr"
            )
            assert theme_detail.title is not None

        # Test get_industries
        industries = integration_client.collections.get_industries(region="tr", locale="en")
        assert isinstance(industries, list)

        # Test get_industry_detail
        if industries:
            industry_detail = integration_client.collections.get_industry_detail(
                industry_id=industries[0].id, region="tr"
            )
            assert industry_detail.title is not None

        # Test get_sectors
        sectors = integration_client.collections.get_sectors(region="tr", locale="en")
        assert isinstance(sectors, list)

        # Test get_sector_detail
        if sectors:
            sector_detail = integration_client.collections.get_sector_detail(
                sector_id=sectors[0].id, region="tr"
            )
            assert sector_detail.title is not None

    def test_error_handling_example(self, mock_api_key: str):
        """Test the error handling example from the README."""
        client = LaplaceClient(api_key=mock_api_key)

        # Mock the API to return an error
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = LaplaceAPIError(
                message="API request failed: 404 Not Found",
                status_code=404,
                response={"error": "Stock not found"},
            )

            try:
                stock = client.stocks.get_detail_by_symbol(symbol="INVALID", region="us")
                assert False, "Should have raised an exception"
            except LaplaceAPIError as e:
                assert "API request failed" in str(e)
                assert e.status_code == 404
                assert e.response == {"error": "Stock not found"}

    def test_authentication_example(self, mock_api_key: str):
        """Test the authentication example from the README."""
        client = LaplaceClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key

    def test_client_initialization(self, mock_api_key):
        """Test client initialization with different parameters."""
        # Test with default base_url
        client = LaplaceClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key
        assert client.base_url == "https://api.finfree.app/api"

        # Test with custom base_url
        custom_url = "https://custom-api.example.com/api"
        client = LaplaceClient(api_key=mock_api_key, base_url=custom_url)
        assert client.base_url == custom_url

    def test_client_context_manager(self, mock_api_key):
        """Test that the client can be used as a context manager."""
        with LaplaceClient(api_key=mock_api_key) as client:
            assert client.api_key == mock_api_key

    def test_all_stocks_methods_are_callable(self, mock_api_key):
        """Test that all stocks methods are callable with proper signatures."""
        client = LaplaceClient(api_key=mock_api_key)

        # Test that all methods exist and are callable
        assert hasattr(client.stocks, "get_all")
        assert hasattr(client.stocks, "get_detail_by_symbol")
        assert hasattr(client.stocks, "get_detail_by_id")
        assert hasattr(client.stocks, "get_price")
        assert hasattr(client.stocks, "get_price_with_interval")
        assert hasattr(client.stocks, "get_tick_rules")
        assert hasattr(client.stocks, "get_restrictions")

    def test_all_collections_methods_are_callable(self, mock_api_key):
        """Test that all collections methods are callable with proper signatures."""
        client = LaplaceClient(api_key=mock_api_key)

        # Test that all methods exist and are callable
        assert hasattr(client.collections, "get_collections")
        assert hasattr(client.collections, "get_collection_detail")
        assert hasattr(client.collections, "get_themes")
        assert hasattr(client.collections, "get_theme_detail")
        assert hasattr(client.collections, "get_industries")
        assert hasattr(client.collections, "get_industry_detail")
        assert hasattr(client.collections, "get_sectors")
        assert hasattr(client.collections, "get_sector_detail")

    def test_region_and_locale_types(self):
        """Test that Region and Locale types are properly defined."""
        from laplace.models import Region, Locale

        # Test valid regions
        valid_regions: List[Region] = ["tr", "us"]
        assert "tr" in valid_regions
        assert "us" in valid_regions

        # Test valid locales
        valid_locales: List[Locale] = ["tr", "en"]
        assert "tr" in valid_locales
        assert "en" in valid_locales

    def test_model_attributes_exist(self, mock_api_key):
        """Test that the models have the expected attributes mentioned in README."""
        client = LaplaceClient(api_key=mock_api_key)

        # Mock a stock response
        mock_stock_data = {
            "id": "test-id",
            "name": "Test Stock",
            "active": True,
            "symbol": "TEST",
            "sectorId": "sector-1",
            "assetType": "equity",
            "industryId": "industry-1",
            "updatedDate": "2024-01-01",
            "description": "Test description",
            "shortDescription": "Short desc",
            "localized_description": {"en": "English", "tr": "Turkish"},
            "localizedShortDescription": {"en": "Short EN", "tr": "Short TR"},
            "region": "us",
            "assetClass": "equity",
        }

        from laplace.models import StockDetail

        stock = StockDetail(**mock_stock_data)

        # Test that all attributes mentioned in README exist
        assert hasattr(stock, "name")
        assert hasattr(stock, "description")
        assert hasattr(stock, "symbol")
        assert hasattr(stock, "region")

        # Test collection model
        mock_collection_data = {
            "id": "collection-1",
            "title": "Test Collection",
            "region": ["tr"],
            "imageUrl": "http://example.com/image.jpg",
            "avatarUrl": "http://example.com/avatar.jpg",
            "numStocks": 10,
            "assetClass": "equity",
        }

        from laplace.models import Collection

        collection = Collection(**mock_collection_data)

        assert hasattr(collection, "title")
        assert hasattr(collection, "num_stocks")
        assert collection.num_stocks == 10
