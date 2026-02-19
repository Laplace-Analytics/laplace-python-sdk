"""Integration tests for stocks client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import AssetType, Currency, Dividend, KeyInsight, PriceCandle, Region, PaginationPageSize, AssetClass, StockPriceData, StockRestriction, StockRules, StockStats, TickRule, TopMover
from laplace.models import (
    Stock,
    StockDetail,
)
from laplace.stocks import IntervalPrice
from tests.conftest import MockResponse


class TestStocksIntegration:
    """Integration tests for stocks client with real API responses."""

    def test_get_all_stocks(self):
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
                "active": True,
            },
            {
                "id": "6203d1ba1e67487527555595",
                "assetType": "stock",
                "name": "Alcoa Corp",
                "symbol": "AA",
                "sectorId": "65533e047844ee7afe9941c0",
                "industryId": "65533e441fa5c7b58afa097d",
                "updatedDate": "2022-02-09T14:37:46.368Z",
                "active": True,
            },
            {
                "id": "675a0087188356cdf4eb535d",
                "assetType": "etf",
                "name": "AXS First Priority CLO Bond ETF",
                "symbol": "AAA",
                "sectorId": "",
                "industryId": "",
                "updatedDate": "2024-12-11T21:13:43.572Z",
                "active": True,
            },
        ]

        client = LaplaceClient(api_key="test-key")

        # Mock the _client.get method
        with patch.object(client, "get", return_value=mock_response_data):
            stocks = client.stocks.get_all(
                region=Region.US, page=1, page_size=PaginationPageSize.PAGE_SIZE_10
            )

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

    def test_get_stock_detail_by_symbol(self):
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
                "tr": "Apple Inc., yenilikçi tüketici elektroniği, yazılım ve hizmetler tasarlayıp geliştiren, önde gelen küresel bir teknoloji şirketidir.\n\n1976 yılında kurulan ve merkezi Cupertino, Kaliforniya'da bulunan Apple, dünyanın en büyük şirketlerinden biridir ve satışlarının çoğunluğunu oluşturan amiral gemisi ürünü iPhone ile tanınır. Şirket, Mac'ler, iPad'ler, Apple Watch'lar ve Apple Music ile iCloud gibi hizmetleri içeren entegre bir ekosistem sunmaktadır. Apple, yazılımını ve yarı iletkenlerini kendi tasarlamakta, ürünlerini Foxconn ve TSMC gibi ortakları aracılığıyla üretmektedir. Şirket, akış hizmetleri, abonelikler ve diğer yeni teknolojiler alanında sunduğu ürünleri genişletmeye devam etmektedir.",
            },
            "region": "us",
            "sectorId": "65533e047844ee7afe9941bf",
            "industryId": "65533e441fa5c7b58afa0972",
            "updatedDate": "2022-02-09T14:37:46.368Z",
            "shortDescription": "Designs and develops consumer electronics, software, and services, including the iPhone, iPad, and Apple Music.",
            "localizedShortDescription": {
                "en": "Designs and develops consumer electronics, software, and services, including the iPhone, iPad, and Apple Music.",
                "tr": "iPhone, iPad ve Apple Music dahil olmak üzere tüketici elektroniği, yazılım ve hizmetleri tasarlar ve geliştirir.",
            },
            "active": True,
        }

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            stock_detail = client.stocks.get_detail_by_symbol(
                symbol="AAPL", region=Region.US, asset_class=AssetClass.EQUITY
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

    def test_get_detail_by_id(self):
        """Test stock detail with localized descriptions and datetime parsing."""
        mock_response_data = {
            "id": "6203d1ba1e6748752755559a",
            "name": "Apple Inc",
            "active": True,
            "region": "us",
            "symbol": "AAPL",
            "sectorId": "tech_sector",
            "industryId": "consumer_elec",
            "assetType": "stock",
            "assetClass": "equity",
            "description": "Long desc",
            "shortDescription": "Short desc",
            "updatedDate": "2024-01-15T12:00:00Z",
            "localized_description": {"en": "English", "tr": "Türkçe"},
            "localizedShortDescription": {"en": "S-English", "tr": "S-Türkçe"}
        }

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            detail = client.stocks.get_detail_by_id(stock_id="6203d1ba1e6748752755559a")

        assert detail.id == "6203d1ba1e6748752755559a"
        assert detail.name == "Apple Inc"
        assert detail.active is True
        assert detail.symbol == "AAPL"

        assert detail.sector_id == "tech_sector"
        assert detail.industry_id == "consumer_elec"  

        assert isinstance(detail.region, Region)
        assert detail.region == Region.US
        assert detail.asset_type == "stock"
        assert isinstance(detail.asset_class, AssetClass)
        assert detail.asset_class == AssetClass.EQUITY

        assert isinstance(detail.updated_date, datetime)
        assert detail.updated_date.year == 2024
        assert detail.updated_date.month == 1
        assert detail.updated_date.day == 15

        assert detail.description == "Long desc"
        assert detail.short_description == "Short desc"

        assert isinstance(detail.localized_description, dict)
        assert detail.localized_description["en"] == "English"
        assert detail.localized_description["tr"] == "Türkçe"
        
        assert isinstance(detail.localized_short_description, dict)
        assert detail.localized_short_description["en"] == "S-English"
        assert detail.localized_short_description["tr"] == "S-Türkçe"
        assert len(detail.localized_short_description) == 2

    def test_get_tick_rules_invalid_region(self):
        """Test that tick rules raises error for non-TR region."""

        client = LaplaceClient(api_key="test-key")

        with pytest.raises(ValueError, match="Tick rules endpoint only works with the 'tr' region"):
            client.stocks.get_tick_rules("AKBNK", region=Region.US)

    def test_get_restrictions_invalid_region(self):
        """Test that restrictions raises error for non-TR region."""

        client = LaplaceClient(api_key="test-key")

        with pytest.raises(
            ValueError, match="Restrictions endpoint only works with the 'tr' region"
        ):
            client.stocks.get_restrictions(symbol="AKBNK", region=Region.US)

    def test_datetime_formatting(self):
        """Test datetime formatting for interval endpoint."""

        client = LaplaceClient(api_key="test-key")

        # Test the internal datetime formatting
        test_dt = datetime(2024, 10, 15, 14, 30, 45)
        formatted = client.stocks._format_datetime(test_dt)

        assert formatted == "2024-10-15 14:30:45"

    def test_get_stock_price(self):
        """Test getting stock price data with aliases (1D, 1W etc.)."""
        mock_response_data = [
            {
                "symbol": "AAPL",
                "1D": [{"c": 150.0, "d": 1634299200.0, "h": 155.0, "l": 149.0, "o": 151.0}],
                "1W": []
            }
        ] 
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            prices = client.stocks.get_price(region=Region.US, symbols=["AAPL"], keys=["1D"])

        assert isinstance(prices, list)
        assert isinstance(prices[0], StockPriceData)
        assert prices[0].symbol == "AAPL"
        assert isinstance(prices[0].one_day, list)
        assert isinstance(prices[0].one_day[0], PriceCandle)
        assert prices[0].one_day[0].close == 150.0
        assert prices[0].one_day[0].date == 1634299200.0
        assert prices[0].one_day[0].high == 155.0
        assert prices[0].one_day[0].low == 149.0
        assert prices[0].one_day[0].open == 151.0


    def test_get_stock_stats(self):
        """Test stock statistics with strict float validation."""
        mock_response_data = [{
            "symbol": "AAPL",
            "eps": 6.57,
            "dayLow": 140.0,
            "dayHigh": 150.0,
            "dayOpen": 145.0,
            "pbRatio": 45.5,
            "peRatio": 28.2,
            "yearLow": 120.0,
            "yearHigh": 160.0,
            "marketCap": 2500000000000.0,
            "ytdReturn": 0.15,
            "3YearReturn": 0.45,
            "5YearReturn": 1.2,
            "latestPrice": 148.5,
            "dailyChange": 0.0214041095890411,
            "3MonthReturn": 0.05,
            "weeklyReturn": 0.02,
            "yearlyReturn": 0.20,
            "monthlyReturn": 0.03,
            "previousClose": 147.0,
            "lowerPriceLimit": 130.0,
            "upperPriceLimit": 170.0
        }]
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            stats = client.stocks.get_stats(symbols=["AAPL"], region=Region.US)

        assert isinstance(stats, list)
        s = stats[0]
        assert isinstance(s, StockStats)

        assert s.symbol == "AAPL"
        assert isinstance(s.eps, float) and s.eps == 6.57

        assert isinstance(s.day_low, float) and s.day_low == 140.0
        assert isinstance(s.day_high, float) and s.day_high == 150.0
        assert isinstance(s.day_open, float) and s.day_open == 145.0
        assert isinstance(s.year_low, float) and s.year_low == 120.0
        assert isinstance(s.year_high, float) and s.year_high == 160.0

        assert isinstance(s.pb_ratio, float) and s.pb_ratio == 45.5
        assert isinstance(s.pe_ratio, float) and s.pe_ratio == 28.2
        assert isinstance(s.market_cap, float) and s.market_cap == 2500000000000.0

        assert isinstance(s.ytd_return, float) and s.ytd_return == 0.15
        assert isinstance(s.three_year_return, float) and s.three_year_return == 0.45  
        assert isinstance(s.five_year_return, float) and s.five_year_return == 1.2    
        assert isinstance(s.three_month_return, float) and s.three_month_return == 0.05
        assert isinstance(s.weekly_return, float) and s.weekly_return == 0.02
        assert isinstance(s.monthly_return, float) and s.monthly_return == 0.03
        assert isinstance(s.yearly_return, float) and s.yearly_return == 0.20

        assert isinstance(s.latest_price, float) and s.latest_price == 148.5
        assert isinstance(s.previous_close, float) and s.previous_close == 147.0
        assert isinstance(s.lower_price_limit, float) and s.lower_price_limit == 130.0
        assert isinstance(s.upper_price_limit, float) and s.upper_price_limit == 170.0

    def test_get_restrictions(self):
        """Test all fields of stock restrictions including datetime and optional fields."""
        mock_response_data = [{
            "id": 12345,
            "title": "VBTS Kapsamında Tedbir",
            "symbol": "THYAO",
            "market": "BIST YILDIZ",
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2024-02-01T00:00:00Z",
            "description": "Açığa satış ve kredili işlem yasağı."
        }]

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            restrictions = client.stocks.get_restrictions(symbol="THYAO", region=Region.TR)

        assert isinstance(restrictions, list)
        res = restrictions[0]
        assert isinstance(res, StockRestriction)

        assert isinstance(res.id, int) and res.id == 12345
        assert isinstance(res.title, str) and len(res.title) > 0
        assert res.symbol == "THYAO"
        assert res.market == "BIST YILDIZ"
        assert isinstance(res.description, str)
        
        assert isinstance(res.start_date, datetime)
        assert res.start_date.year == 2024
        assert isinstance(res.end_date, datetime)

    def test_get_all_restrictions(self):
        """Test all fields of stock restrictions including datetime and optional fields."""
        mock_response_data = [{
            "id": 12345,
            "title": "VBTS Kapsamında Tedbir",
            "symbol": "THYAO",
            "market": "BIST YILDIZ",
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2024-02-01T00:00:00Z",
            "description": "Açığa satış ve kredili işlem yasağı."
        }]

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            restrictions = client.stocks.get_all_restrictions(region=Region.TR)

        assert isinstance(restrictions, list)
        res = restrictions[0]
        assert isinstance(res, StockRestriction)

        assert isinstance(res.id, int) and res.id == 12345
        assert isinstance(res.title, str) and len(res.title) > 0
        assert res.symbol == "THYAO"
        assert res.market == "BIST YILDIZ"
        assert isinstance(res.description, str)
        
        assert isinstance(res.start_date, datetime)
        assert res.start_date.year == 2024
        assert isinstance(res.end_date, datetime)

    def test_get_price_with_interval(self):
        """Test historical price interval with candle aliases and date formatting."""
        mock_response_data = [
            {
                "c": 53.5,
                "d": 1743664260,
                "h": 53.5,
                "l": 51.4,
                "o": 52,
                "uc": 53.5,
                "uh": 53.5,
                "ul": 51.4,
                "uo": 52
            }
        ]
        
        from_dt = datetime(2024, 1, 1, 10, 0, 0)
        to_dt = datetime(2024, 1, 2, 10, 0, 0)
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            candles = client.stocks.get_price_with_interval(
                symbol="AAPL",
                region=Region.US,
                from_date=from_dt,
                to_date=to_dt,
                interval=IntervalPrice.ONE_HOUR
            )
            
        assert isinstance(candles, list)
        assert len(candles) == 1
        c = candles[0]
        assert isinstance(c, PriceCandle)
        
        assert isinstance(c.close, float) and c.close == 53.5
        assert isinstance(c.date, (float, int)) and c.date == 1743664260
        assert isinstance(c.high, float) and c.high == 53.5
        assert isinstance(c.low, float) and c.low == 51.4
        assert isinstance(c.open, float) and c.open == 52.0

        assert isinstance(c.unadjusted_close, float) and c.unadjusted_close == 53.5
        assert isinstance(c.unadjusted_high, float) and c.unadjusted_high == 53.5
        assert isinstance(c.unadjusted_low, float) and c.unadjusted_low == 51.4
        assert isinstance(c.unadjusted_open, float) and c.unadjusted_open == 52.0

        assert c.volume is None
        assert c.unadjusted_volume is None

    def test_get_dividends(self):
        """Test dividend model and datetime parsing."""
        mock_response_data = [{
            "date": "2023-11-10T00:00:00Z",
            "currency": "TRY",
            "netRatio": 0.15,
            "netAmount": 1.5,
            "priceThen": 150.0,
            "grossRatio": 0.17,
            "grossAmount": 1.7,
            "stoppageRatio": 0.02,
            "stoppageAmount": 0.2
        }]
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            dividends = client.stocks.get_dividends(symbol="AAPL", region=Region.US)

        assert isinstance(dividends, list)
        assert len(dividends) == 1
        
        d = dividends[0]
        assert isinstance(d, Dividend)

        assert isinstance(d.date, datetime)
        assert d.date.year == 2023
        assert d.date.month == 11
        assert d.date.day == 10

        assert isinstance(d.net_ratio, float)
        assert d.net_ratio == 0.15
        assert isinstance(d.net_amount, float)
        assert d.net_amount == 1.5

        assert isinstance(d.gross_ratio, float)
        assert d.gross_ratio == 0.17
        assert isinstance(d.gross_amount, float)
        assert d.gross_amount == 1.7

        assert isinstance(d.stoppage_ratio, float)
        assert d.stoppage_ratio == 0.02
        assert isinstance(d.stoppage_amount, float)
        assert d.stoppage_amount == 0.2

        assert isinstance(d.price_then, float)
        assert d.price_then == 150.0

    def test_get_top_movers(self):
        """Test all fields of top movers including float changes and enum mapping."""
        mock_response_data = [{
            "change": 9.85,
            "symbol": "AKBNK",
            "assetType": "stock",
            "assetClass": "equity"
        }]

        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            movers = client.stocks.get_top_movers(region=Region.TR, direction="gainers")

        assert isinstance(movers, list)
        mover = movers[0]
        assert isinstance(mover, TopMover)

        assert isinstance(mover.change, float) and mover.change == 9.85
        assert mover.symbol == "AKBNK"
        
        assert isinstance(mover.asset_type, AssetType)
        assert isinstance(mover.asset_class, AssetClass)

    def test_get_tick_rules(self):
        """Test tick rules and price limits for TR region."""
        mock_response_data = {
            "rules": [
                {"priceFrom": 0.0, "priceTo": 20.0, "tickSize": 0.01}
            ],
            "basePrice": 15.5,
            "additionalPrice": 0,
            "lowerPriceLimit": 13.95,
            "upperPriceLimit": 17.05
        }
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            rules = client.stocks.get_tick_rules(symbol="AKBNK", region=Region.TR)

        assert isinstance(rules, StockRules)
        
        assert isinstance(rules.base_price, float) and rules.base_price == 15.5
        assert isinstance(rules.additional_price, int) and rules.additional_price == 0
        assert isinstance(rules.lower_price_limit, float) and rules.lower_price_limit == 13.95
        assert isinstance(rules.upper_price_limit, float) and rules.upper_price_limit == 17.05

        assert isinstance(rules.rules, list)
        assert len(rules.rules) == 1
        
        r = rules.rules[0]
        assert isinstance(r, TickRule)
        assert isinstance(r.price_from, float) and r.price_from == 0.0
        assert isinstance(r.price_to, float) and r.price_to == 20.0
        assert isinstance(r.tick_size, float) and r.tick_size == 0.01

    def test_get_key_insight(self):
        """Test key insights model."""
        mock_response_data = {
            "symbol": "AAPL",
            "insight": "Apple shows strong growth in services."
        }
        
        client = LaplaceClient(api_key="test-key")
        with patch.object(client, "get", return_value=mock_response_data):
            insight = client.stocks.get_key_insight(symbol="AAPL", region=Region.US)

        assert isinstance(insight, KeyInsight)
        
        assert isinstance(insight.symbol, str) and insight.symbol == "AAPL"
        assert isinstance(insight.insight, str) and insight.insight == "Apple shows strong growth in services."
        assert len(insight.insight) > 0


class TestStocksRealIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_all_stocks(self, integration_client: LaplaceClient):
        """Test real API call for getting all stocks."""
        stocks = integration_client.stocks.get_all(
            region=Region.US, page=1, page_size=PaginationPageSize.PAGE_SIZE_10
        )

        assert len(stocks) > 0
        assert len(stocks) <= 10
        
        for stock in stocks:
            assert isinstance(stock, Stock)
            assert isinstance(stock.id, str)
            assert isinstance(stock.name, str)
            assert isinstance(stock.active, bool)
            assert isinstance(stock.symbol, str)           
            assert isinstance(stock.sector_id, str)
            assert isinstance(stock.industry_id, str)           
            assert isinstance(stock.asset_type, AssetType)
            assert isinstance(stock.updated_date, datetime)
            assert len(stock.id) > 0
            assert len(stock.symbol) > 0

    @pytest.mark.integration
    def test_real_get_stock_detail_by_symbol(self, integration_client: LaplaceClient):
        """Test real API call for getting stock detail by symbol."""
        stock_detail = integration_client.stocks.get_detail_by_symbol(
            symbol="AAPL", region=Region.US, asset_class=AssetClass.EQUITY
        )

        assert isinstance(stock_detail, StockDetail)
        assert stock_detail.symbol == "AAPL"
        assert stock_detail.region == Region.US.value
        assert stock_detail.active == True
        assert stock_detail.asset_class == AssetClass.EQUITY.value
        assert stock_detail.asset_type == AssetType.STOCK.value
        assert isinstance(stock_detail.industry_id, str)
        assert isinstance(stock_detail.sector_id, str)
        assert isinstance(stock_detail.name, str)
        assert isinstance(stock_detail.description, str)
        assert isinstance(stock_detail.short_description, str)
        assert isinstance(stock_detail.localized_description, dict)
        assert isinstance(stock_detail.localized_short_description, dict)
        assert "en" in stock_detail.localized_description
        assert "tr" in stock_detail.localized_description
        assert isinstance(stock_detail.localized_description["en"], str)

    @pytest.mark.integration
    def test_real_get_detail_by_id(self, integration_client: LaplaceClient):
        target_id = "6203d1ba1e6748752755559a"
        
        stock_detail = integration_client.stocks.get_detail_by_id(stock_id=target_id)
        assert stock_detail.id == target_id
        assert isinstance(stock_detail, StockDetail)
        assert stock_detail.symbol == "AAPL"
        assert stock_detail.region == Region.US.value
        assert stock_detail.active == True
        assert stock_detail.asset_class == AssetClass.EQUITY.value
        assert stock_detail.asset_type == AssetType.STOCK.value
        assert isinstance(stock_detail.industry_id, str)
        assert isinstance(stock_detail.sector_id, str)
        assert isinstance(stock_detail.name, str)
        assert isinstance(stock_detail.description, str)
        assert isinstance(stock_detail.short_description, str)
        assert isinstance(stock_detail.localized_description, dict)
        assert isinstance(stock_detail.localized_short_description, dict)
        assert "en" in stock_detail.localized_description
        assert "tr" in stock_detail.localized_description
        assert isinstance(stock_detail.localized_description["en"], str)


    @pytest.mark.integration
    def test_real_get_stats(self, integration_client: LaplaceClient):
        stats = integration_client.stocks.get_stats(symbols=["ASELS"], region=Region.TR)
        assert len(stats) > 0
        s = stats[0]
        assert s.symbol == "ASELS"
        assert isinstance(s.previous_close, float)
        assert isinstance(s.ytd_return, float)
        assert isinstance(s.yearly_return, float)
        assert isinstance(s.market_cap, float)
        assert isinstance(s.pe_ratio, float)
        assert isinstance(s.pb_ratio, float)
        assert isinstance(s.year_low, float)
        assert isinstance(s.year_high, float)
        assert isinstance(s.three_year_return, float)
        assert isinstance(s.five_year_return, float)
        assert isinstance(s.three_month_return, float)
        assert isinstance(s.monthly_return, float)
        assert isinstance(s.weekly_return, float)
        assert isinstance(s.latest_price, float)
        assert isinstance(s.daily_change, float)
        assert isinstance(s.day_high, float)
        assert isinstance(s.day_low, float)
        assert isinstance(s.lower_price_limit, float)
        assert isinstance(s.upper_price_limit, float)
        assert isinstance(s.day_open, float)
        assert isinstance(s.eps, float)


    @pytest.mark.integration
    def test_real_get_price(self, integration_client: LaplaceClient):
        prices = integration_client.stocks.get_price(
            region=Region.US, symbols=["AAPL"], keys=["1D"]
        )
        assert len(prices) > 0
        p = prices[0]
        assert p.symbol == "AAPL"
        assert isinstance(p.one_day, list)
        if p.one_day:
            candle = p.one_day[0]
            assert isinstance(candle, PriceCandle)
            assert isinstance(candle.close, float)
            assert isinstance(candle.date, float)
            assert isinstance(candle.high, float)
            assert isinstance(candle.low, float)
            assert isinstance(candle.open, float)

        timeframe_fields = {
            "one_week": p.one_week,
            "one_month": p.one_month,
            "three_month": p.three_months,           
            "one_year": p.one_year,
            "two_year": p.two_years,
            "three_year": p.three_years,
            "five_year": p.five_years,
        }

        for field_name, value in timeframe_fields.items():
            assert not value, f"Expected {field_name} to be empty, but it contains data."

    @pytest.mark.integration
    def test_real_get_price_with_interval(self, integration_client: LaplaceClient):
        candles = integration_client.stocks.get_price_with_interval(
            symbol="ASELS",
            region=Region.TR,
            from_date=datetime(2025, 5, 1),
            to_date=datetime(2025, 5, 5),
            interval=IntervalPrice.ONE_DAY,
            detail=True
        )

        assert len(candles) > 0
        first_candle = candles[0]
        assert isinstance(first_candle, PriceCandle)
        assert isinstance(first_candle.close, float)
        assert isinstance(first_candle.date, float)
        assert isinstance(first_candle.high, float)
        assert isinstance(first_candle.low, float)
        assert isinstance(first_candle.open, float)
        assert isinstance(first_candle.volume, float)
        assert isinstance(first_candle.unadjusted_open, float)
        assert isinstance(first_candle.unadjusted_high, float)
        assert isinstance(first_candle.unadjusted_low, float)
        assert isinstance(first_candle.unadjusted_close, float)
        assert isinstance(first_candle.unadjusted_volume, float)


    @pytest.mark.integration
    def test_real_get_dividends(self, integration_client: LaplaceClient):
        dividends = integration_client.stocks.get_dividends(symbol="ASELS", region=Region.TR)
        assert isinstance(dividends, list)
        if dividends:
            d = dividends[0]
            assert isinstance(d, Dividend)
            assert isinstance(d.date, datetime)
            assert isinstance(d.net_amount, float)
            assert d.currency == Currency.TRY.value
            assert isinstance(d.net_ratio, float)
            assert isinstance(d.gross_amount, float)
            assert isinstance(d.gross_ratio, float)
            assert isinstance(d.price_then, float)
            assert isinstance(d.stoppage_amount, float)
            assert isinstance(d.stoppage_ratio, float)

    @pytest.mark.integration
    def test_real_get_tick_rules(self, integration_client: LaplaceClient):
        rules = integration_client.stocks.get_tick_rules(symbol="ASELS", region=Region.TR)
        assert isinstance(rules, StockRules)
        assert isinstance(rules.base_price, float)
        assert isinstance(rules.additional_price, int)
        assert isinstance(rules.lower_price_limit, float)
        assert isinstance(rules.upper_price_limit, float)

        assert len(rules.rules) > 0
        first_rule = rules.rules[0]
        assert isinstance(first_rule, TickRule)
        assert isinstance(first_rule.price_from, float)
        assert isinstance(first_rule.price_to, float)
        assert isinstance(first_rule.tick_size, float)


    @pytest.mark.integration
    def test_real_get_restrictions(self, integration_client: LaplaceClient):
        res = integration_client.stocks.get_restrictions(symbol="ASELS", region=Region.TR)
        assert isinstance(res, list)

    @pytest.mark.integration
    def test_real_get_all_restrictions(self, integration_client: LaplaceClient):
        res = integration_client.stocks.get_all_restrictions(region=Region.TR)
        assert isinstance(res, list)

    @pytest.mark.integration
    def test_real_get_top_movers(self, integration_client: LaplaceClient):
        movers = integration_client.stocks.get_top_movers(region=Region.US, direction="gainers")
        assert len(movers) > 0
        first_mover = movers[0]
        assert isinstance(first_mover, TopMover)
        assert first_mover.change > 0
        assert isinstance(first_mover.symbol, str)
        assert first_mover.asset_type == AssetType.STOCK.value
        assert first_mover.asset_class == AssetClass.EQUITY.value


    @pytest.mark.integration
    def test_real_get_key_insight(self, integration_client: LaplaceClient):
        insight = integration_client.stocks.get_key_insight(symbol="AAPL", region=Region.US)
        assert isinstance(insight, KeyInsight)
        assert insight.symbol == "AAPL"
        assert isinstance(insight.insight, str)
