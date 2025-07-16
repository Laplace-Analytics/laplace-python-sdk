"""Integration tests for stocks client."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from laplace import LaplaceClient
from laplace.stocks import HistoricalPriceInterval
from laplace.models import Stock, StockDetail, StockPriceData, PriceCandle, StockRules, StockRestriction
from tests.conftest import MockResponse


class TestStocksIntegration:
    """Integration tests for stocks client with real API responses."""
    
    @patch('httpx.Client')
    def test_get_all_stocks(self, mock_httpx_client):
        """Test getting all stocks with real API response."""
        # Real API response from /api/v2/stock/all?page=1&pageSize=5&region=us
        mock_response_data = [
            {
                "id": "6203d1ba1e67487527555594",
                "assetType": "stock",
                "name": "Agilent Technologies Inc.",
                "symbol": "A",
                "sectorId": "65533e047844ee7afe9941bd",
                "industryId": "65533e441fa5c7b58afa0962",
                "updatedDate": "2022-02-09T14:37:46.368Z",
                "active": True
            },
            {
                "id": "6203d1ba1e67487527555595",
                "assetType": "stock",
                "name": "Alcoa Corp",
                "symbol": "AA",
                "sectorId": "65533e047844ee7afe9941c0",
                "industryId": "65533e441fa5c7b58afa097d",
                "updatedDate": "2022-02-09T14:37:46.368Z",
                "active": True
            },
            {
                "id": "675a0087188356cdf4eb535d",
                "assetType": "etf",
                "name": "AXS First Priority CLO Bond ETF",
                "symbol": "AAA",
                "sectorId": "",
                "industryId": "",
                "updatedDate": "2024-12-11T21:13:43.572Z",
                "active": True
            }
        ]
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance
        
        client = LaplaceClient(api_key="test-key")
        
        # Mock the _client.get method
        with patch.object(client, 'get', return_value=mock_response_data):
            stocks = client.stocks.get_all(region="us", page=1, page_size=5)
        
        # Assertions
        assert len(stocks) == 3
        assert isinstance(stocks[0], Stock)
        assert stocks[0].symbol == "A"
        assert stocks[0].name == "Agilent Technologies Inc."
        assert stocks[0].asset_type == "stock"
        assert stocks[0].active is True
        assert stocks[0].sector_id == "65533e047844ee7afe9941bd"
        assert stocks[0].industry_id == "65533e441fa5c7b58afa0962"
        
        assert stocks[1].symbol == "AA"
        assert stocks[1].name == "Alcoa Corp"
        assert stocks[1].asset_type == "stock"
        
        # Test ETF as well
        assert stocks[2].symbol == "AAA"
        assert stocks[2].asset_type == "etf"
        assert stocks[2].sector_id == ""  # ETFs have empty sector/industry

    @patch('httpx.Client')
    def test_get_stock_detail_by_symbol(self, mock_httpx_client):
        """Test getting stock detail by symbol with real API response."""
        # Real API response from /api/v1/stock/detail?symbol=AAPL&region=us&asset_class=equity
        mock_response_data = {
            "id": "6203d1ba1e6748752755559a",
            "assetType": "stock",
            "assetClass": "equity",
            "name": "Apple Inc",
            "symbol": "AAPL",
            "description": "Apple Inc. is a leading global technology company known for designing and developing a wide range of innovative consumer electronics, software, and services.\n\nFounded in 1976 and headquartered in Cupertino, California, Apple is among the world's largest companies, with the iPhone as its flagship product making up the majority of its sales. It offers an integrated ecosystem that includes Macs, iPads, Apple Watches, and services like Apple Music and iCloud. Apple designs its own software and semiconductors, with products manufactured through partners like Foxconn and TSMC. The company continues to expand its offerings in streaming, subscriptions, and other new technologies.",
            "localized_description": {
                "def": "Apple Inc., yenilikçi tüketici elektroniği, yazılım ve hizmetler tasarlayıp geliştiren, önde gelen küresel bir teknoloji şirketidir.\n\n1976 yılında kurulan ve merkezi Cupertino, Kaliforniya'da bulunan Apple, dünyanın en büyük şirketlerinden biridir ve satışlarının çoğunluğunu oluşturan amiral gemisi ürünü iPhone ile tanınır. Şirket, Mac'ler, iPad'ler, Apple Watch'lar ve Apple Music ile iCloud gibi hizmetleri içeren entegre bir ekosistem sunmaktadır. Apple, yazılımını ve yarı iletkenlerini kendi tasarlamakta, ürünlerini Foxconn ve TSMC gibi ortakları aracılığıyla üretmektedir. Şirket, akış hizmetleri, abonelikler ve diğer yeni teknolojiler alanında sunduğu ürünleri genişletmeye devam etmektedir.",
                "en": "Apple Inc. is a leading global technology company known for designing and developing a wide range of innovative consumer electronics, software, and services.\n\nFounded in 1976 and headquartered in Cupertino, California, Apple is among the world's largest companies, with the iPhone as its flagship product making up the majority of its sales. It offers an integrated ecosystem that includes Macs, iPads, Apple Watches, and services like Apple Music and iCloud. Apple designs its own software and semiconductors, with products manufactured through partners like Foxconn and TSMC. The company continues to expand its offerings in streaming, subscriptions, and other new technologies.",
                "tr": "Apple Inc., yenilikçi tüketici elektroniği, yazılım ve hizmetler tasarlayıp geliştiren, önde gelen küresel bir teknoloji şirketidir.\n\n1976 yılında kurulan ve merkezi Cupertino, Kaliforniya'da bulunan Apple, dünyanın en büyük şirketlerinden biridir ve satışlarının çoğunluğunu oluşturan amiral gemisi ürünü iPhone ile tanınır. Şirket, Mac'ler, iPad'ler, Apple Watch'lar ve Apple Music ile iCloud gibi hizmetleri içeren entegre bir ekosistem sunmaktadır. Apple, yazılımını ve yarı iletkenlerini kendi tasarlamakta, ürünlerini Foxconn ve TSMC gibi ortakları aracılığıyla üretmektedir. Şirket, akış hizmetleri, abonelikler ve diğer yeni teknolojiler alanında sunduğu ürünleri genişletmeye devam etmektedir."
            },
            "region": "us",
            "sectorId": "65533e047844ee7afe9941bf",
            "industryId": "65533e441fa5c7b58afa0972",
            "updatedDate": "2022-02-09T14:37:46.368Z",
            "shortDescription": "Designs and develops consumer electronics, software, and services, including the iPhone, iPad, and Apple Music.",
            "localizedShortDescription": {
                "en": "Designs and develops consumer electronics, software, and services, including the iPhone, iPad, and Apple Music.",
                "tr": "iPhone, iPad ve Apple Music dahil olmak üzere tüketici elektroniği, yazılım ve hizmetleri tasarlar ve geliştirir."
            },
            "active": True
        }
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance
        
        client = LaplaceClient(api_key="test-key")
        
        with patch.object(client, 'get', return_value=mock_response_data):
            stock_detail = client.stocks.get_detail_by_symbol(
                symbol="AAPL", 
                region="us", 
                asset_class="equity"
            )
        
        # Assertions
        assert isinstance(stock_detail, StockDetail)
        assert stock_detail.symbol == "AAPL"
        assert stock_detail.name == "Apple Inc"
        assert stock_detail.region == "us"
        assert stock_detail.asset_class == "equity"
        assert stock_detail.asset_type == "stock"
        assert stock_detail.active is True
        assert stock_detail.sector_id == "65533e047844ee7afe9941bf"
        assert stock_detail.industry_id == "65533e441fa5c7b58afa0972"
        
        # Test description fields
        assert "Apple Inc. is a leading global technology company" in stock_detail.description
        assert "iPhone, iPad, and Apple Music" in stock_detail.short_description
        
        # Test localized descriptions
        assert "def" in stock_detail.localized_description
        assert "en" in stock_detail.localized_description
        assert "tr" in stock_detail.localized_description
        assert "en" in stock_detail.localized_short_description
        assert "tr" in stock_detail.localized_short_description
        
        # Test Turkish descriptions
        assert "teknoloji şirketidir" in stock_detail.localized_description["tr"]
        assert "tüketici elektroniği" in stock_detail.localized_short_description["tr"]

    @patch('httpx.Client')
    def test_get_tick_rules_invalid_region(self, mock_httpx_client):
        """Test that tick rules raises error for non-TR region."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        
        client = LaplaceClient(api_key="test-key")
        
        with pytest.raises(ValueError, match="Tick rules endpoint only works with the 'tr' region"):
            client.stocks.get_tick_rules(region="us")

    @patch('httpx.Client')
    def test_get_restrictions_invalid_region(self, mock_httpx_client):
        """Test that restrictions raises error for non-TR region."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        
        client = LaplaceClient(api_key="test-key")
        
        with pytest.raises(ValueError, match="Restrictions endpoint only works with the 'tr' region"):
            client.stocks.get_restrictions(region="us")

    @patch('httpx.Client')
    def test_datetime_formatting(self, mock_httpx_client):
        """Test datetime formatting for interval endpoint."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        
        client = LaplaceClient(api_key="test-key")
        
        # Test the internal datetime formatting
        test_dt = datetime(2024, 10, 15, 14, 30, 45)
        formatted = client.stocks._format_datetime(test_dt)
        
        assert formatted == "2024-10-15 14:30:45"


class TestStocksRealIntegration:
    """Real integration tests (requires API key)."""
    
    @pytest.mark.integration
    def test_real_get_all_stocks(self, integration_client):
        """Test real API call for getting all stocks."""
        stocks = integration_client.stocks.get_all(region="us", page=1, page_size=5)
        
        assert len(stocks) <= 5  # Should return at most 5 stocks
        assert all(isinstance(stock, Stock) for stock in stocks)
        assert all(stock.symbol for stock in stocks)  # All should have symbols
        assert all(stock.name for stock in stocks)  # All should have names
        assert all(stock.asset_type for stock in stocks)  # All should have asset types
    
    @pytest.mark.integration
    def test_real_get_stock_detail_by_symbol(self, integration_client):
        """Test real API call for getting stock detail by symbol."""
        stock_detail = integration_client.stocks.get_detail_by_symbol(
            symbol="AAPL", 
            region="us", 
            asset_class="equity"
        )
        
        assert isinstance(stock_detail, StockDetail)
        assert stock_detail.symbol == "AAPL"
        assert stock_detail.region == "us"
        assert stock_detail.asset_class == "equity"
        assert stock_detail.name  # Should have a name
        assert stock_detail.description  # Should have description
        assert stock_detail.localized_description  # Should have localized descriptions