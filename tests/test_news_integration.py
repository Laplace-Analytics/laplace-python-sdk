from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    News,
    NewsCategoryListItem,
    NewsHighlight,
    NewsLane,
    NewsLaneListItem,
    NewsType,
    NewsOrderBy,
    Region,
    PaginationPageSize,
    PaginatedResponse,
    SortDirection,
)
from tests.conftest import MockResponse


class TestNewsUnit:
    """Unit tests for news client with mocked responses."""

    @patch("httpx.Client")
    def test_get_news(self, mock_httpx_client):
        """Test getting paginated news with real API response."""
        mock_response_data = {
            "recordCount": 352,
            "items": [
                {
                    "url": "https://www.reuters.com/business/energy/commonwealth-lng-wants-more-time-build-planned-export-facility-louisiana-2025-10-07/",
                    "content": {
                        "title": "Commonwealth LNG wants more time to build planned export facility in Louisiana",
                        "content": [
                            "Commonwealth LNG has requested a four-year extension from federal regulators to construct & begin exporting liquefied natural gas from a proposed facility in Cameron Parish, Louisiana.",
                            "The extension request is due to an approval pause by former U.S. President Joe Biden; although lifted by President Donald Trump, the company cannot meet the current deadline of November 2027.",
                        ],
                        "summary": [
                            "Commonwealth LNG has requested a four-year extension from federal regulators.",
                            "The company has sold 5 million metric tons per annum of planned capacity.",
                        ],
                        "description": "Commonwealth LNG has asked federal regulators for a four-year extension to construct and begin exporting liquefied natural gas.",
                        "investorInsight": "What it means for investors: The extension request could postpone the start of export revenues and delay expected cash flows.",
                    },
                    "sectors": {
                        "name": "Energy",
                        "meanType": 9,
                        "newsCount": 1,
                    },
                    "tickers": [
                        {
                            "id": "6203d1ba1e674875275558f7",
                            "name": "EQT Corp",
                            "symbol": "EQT",
                        }
                    ],
                    "imageUrl": "",
                    "createdAt": "2025-10-07T17:10:01.560644Z",
                    "publisher": {
                        "name": "Reuters",
                        "logoUrl": None,
                    },
                    "timestamp": "2025-10-07T16:50:16Z",
                    "categories": {
                        "name": "Sector News",
                        "newsCount": 1,
                        "categoryType": "StockSpesific",
                    },
                    "industries": {
                        "name": "Oil/Gas (Production and Exploration)",
                        "meanType": 78,
                    },
                    "publisherUrl": "Reuters",
                    "qualityScore": 0,
                    "relatedTickers": [
                        {
                            "id": "6203d1ba1e674875275558f7",
                            "name": "EQT Corp",
                            "symbol": "EQT",
                        }
                    ],
                }
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.news.get_news(
                locale="en",
                region=Region.US,
                page=0,
                page_size=PaginationPageSize.PAGE_SIZE_10,
            )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 352
        assert len(response.items) == 1
        assert all(isinstance(item, News) for item in response.items)

        news = response.items[0]
        assert isinstance(news.created_at, datetime)
        assert news.url == "https://www.reuters.com/business/energy/commonwealth-lng-wants-more-time-build-planned-export-facility-louisiana-2025-10-07/"
        assert news.image_url == ""
        assert isinstance(news.timestamp, datetime)
        assert news.publisher_url == "Reuters"
        assert news.publisher.name == "Reuters"
        assert news.publisher.logo_url is None
        assert news.quality_score == 0

        assert news.content is not None
        assert news.content.title == "Commonwealth LNG wants more time to build planned export facility in Louisiana"
        assert len(news.content.content) == 2
        assert len(news.content.summary) == 2
        assert news.content.investor_insight.startswith("What it means for investors:")

        assert len(news.related_tickers) == 1
        assert news.related_tickers[0].symbol == "EQT"
        assert len(news.tickers) == 1
        assert news.tickers[0].name == "EQT Corp"

        assert news.categories.news_count == 1
        assert news.categories.category_type == "StockSpesific"
        assert news.sectors.mean_type == 9 
        assert news.industries.mean_type == 78 

    @patch("httpx.Client")
    def test_get_news_with_filters(self, mock_httpx_client):
        """Test getting news with optional filters."""
        mock_response_data = {
            "recordCount": 1,
            "items": [
                {
                    "createdAt": "2025-07-15T10:00:00.000Z",
                    "url": "https://example.com/news/1",
                    "imageUrl": "https://example.com/img/1.jpg",
                    "timestamp": "2025-07-15T09:30:00.000Z",
                    "publisherUrl": "https://example.com",
                    "publisher": {"name": "Bloomberg", "logoUrl": None},
                    "relatedTickers": [],
                    "tickers": None,
                    "categories": None,
                    "sectors": None,
                    "content": None,
                    "industries": None,
                    "qualityScore": 70,
                },
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            response = client.news.get_news(
                locale="tr",
                region=Region.US,
                news_type=NewsType.BLOOMBERG,
                news_order_by=NewsOrderBy.TIMESTAMP,
                direction=SortDirection.DESC,
                page=0,
                page_size=PaginationPageSize.PAGE_SIZE_10,
            )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count == 1
        assert len(response.items) == 1

    @patch("httpx.Client")
    def test_get_highlights(self, mock_httpx_client):
        """Test getting news highlights with real API response."""
        mock_response_data = {
            "tech": [
                "Alphabet ve Amazon'un desteğiyle Anthropic, 2026 başlarında Hindistan'ın Bengaluru kentinde bir ofis açacak.",
                "Elon Musk'ın xAI'si, GPU kullanımıyla bağlantılı olarak Nvidia yatırımıyla 20 milyar dolar finansman hedefliyor.",
                "Intel'in yeni Panther Lake çipi, 2026 başında piyasaya sunulacak; zararlar arasında enerji tasarrufu ve performans artışı vaat ediyor.",
            ],
            "other": [
                "ABD Yüksek Mahkemesi, Epic Games'in davası kapsamında Google'ın Play uygulamalarındaki değişikliği engellemeyecek.",
                "Mars, pazar payını genişleterek Kellanova'yı 36 milyar dolara satın alacak.",
            ],
            "finance": [
                "Fifth Third Bank, Comerica'yı 10,9 milyar dolara satın alacak ve böylece ABD'nin 9. en büyük bankası olacak.",
                "JPMorgan Chase, SEC'in çeyreklik kazanç raporlarını gevşetmesini destekliyor ve yılda 2 milyar dolar yapay zekaya yatırım yapıyor.",
            ],
            "consumer": [
                "Tesla, rekabet ortamında pazar payını geri almak için daha ucuz Model Y ve Model 3'ü piyasaya sürdü.",
            ],
            "healthcare": [
                "İlaç üreticileri, Trump'ın ilaç fiyatlarını düşürme planıyla uyumlu olarak tele-sağlık satışlarını artırıyor.",
            ],
            "energyAndUtilities": [
                "ABD Enerji Bakanlığı, Stellantis ve GM'ye verilen 1,1 milyar dolarlık hibeleri iptal edebilir.",
                "Ekonomik belirsizlikle desteklenen altın fiyatları yükseldi; tahminler daha fazla artış öngörüyor.",
            ],
            "industrialsAndMaterials": [
                "Boeing, bir grevi sona erdirmek için IAM Sendikası ile geçici bir anlaşmaya vardı.",
                "Airbus A320, güçlü satışlardan faydalanarak teslimat sayısında Boeing 737'yi geride bıraktı.",
            ],
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            highlights = client.news.get_highlights(
                locale="tr", region=Region.US
            )

        assert isinstance(highlights, NewsHighlight)
        assert len(highlights.tech) == 3
        assert len(highlights.other) == 2
        assert len(highlights.finance) == 2
        assert len(highlights.consumer) == 1
        assert len(highlights.healthcare) == 1
        assert len(highlights.energy_and_utilities) == 2
        assert len(highlights.industrials_and_materials) == 2

    @patch("httpx.Client")
    def test_get_news_with_extra_filters(self, mock_httpx_client):
        """Test that extra_filters parameter is passed correctly (v1)."""
        mock_response_data = {"recordCount": 0, "items": []}

        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            client.news.get_news(
                locale="en",
                region=Region.US,
                extra_filters="symbol eq AAPL",
            )

        call_params = mock_get.call_args
        assert call_params[1]["params"]["extraFilters"] == "symbol eq AAPL"

    @patch("httpx.Client")
    def test_get_news_v1_with_lane_and_filters(self, mock_httpx_client):
        """Test that v1 get_news forwards lane and the individual filters."""
        mock_response_data = {"recordCount": 0, "items": []}

        mock_httpx_client.return_value = Mock()
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            client.news.get_news(
                locale="en",
                region=Region.US,
                lane=NewsLane.FAST_MOVERS,
                symbols="AAPL",
                categories="Technology",
                sectors="Technology",
                industries="Semiconductors",
                quality_score_min=5,
                quality_score_max=10,
                timestamp_from="2026-06-01",
                timestamp_to="2026-06-30",
            )

        path, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
        params = kwargs["params"]
        assert path == "v1/news"
        assert params["lane"] == "fast_movers"
        assert params["symbols"] == "AAPL"
        assert params["categories"] == "Technology"
        assert params["sectors"] == "Technology"
        assert params["industries"] == "Semiconductors"
        assert params["qualityScoreMin"] == 5
        assert params["qualityScoreMax"] == 10
        assert params["timestampFrom"] == "2026-06-01"
        assert params["timestampTo"] == "2026-06-30"
        assert "extraFilters" not in params

    @patch("httpx.Client")
    def test_get_news_v2_with_lane(self, mock_httpx_client):
        """Test that v2 get_news_v2 forwards the lane filter."""
        mock_response_data = {"recordCount": 0, "items": []}

        mock_httpx_client.return_value = Mock()
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            client.news.get_news_v2(
                locale="en",
                region=Region.US,
                lane=NewsLane.GLOBAL_MACRO,
            )

        path, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
        params = kwargs["params"]
        assert path == "v2/news"
        assert params["lane"] == "global_macro"

    @patch("httpx.Client")
    def test_get_news_v2_with_filters(self, mock_httpx_client):
        """Test that the v2 individual filter parameters are passed correctly."""
        mock_response_data = {"recordCount": 0, "items": []}

        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            client.news.get_news_v2(
                locale="en",
                region=Region.US,
                news_order_by=NewsOrderBy.QUALITY_SCORE,
                direction=SortDirection.DESC,
                symbols="AAPL,MSFT",
                sectors="Technology",
                categories="Sector News",
                industries="Software",
                quality_score_min=7,
                quality_score_max=10,
                timestamp_from="2026-05-01",
                timestamp_to="2026-06-01",
            )

        path, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
        params = kwargs["params"]
        assert path == "v2/news"
        assert params["orderBy"] == "quality_score"
        assert params["orderByDirection"] == "desc"
        assert params["symbols"] == "AAPL,MSFT"
        assert params["sectors"] == "Technology"
        assert params["categories"] == "Sector News"
        assert params["industries"] == "Software"
        assert params["qualityScoreMin"] == 7
        assert params["qualityScoreMax"] == 10
        assert params["timestampFrom"] == "2026-05-01"
        assert params["timestampTo"] == "2026-06-01"
        assert "extraFilters" not in params

    @patch("httpx.Client")
    def test_get_news_categories(self, mock_httpx_client):
        """Test getting the canonical news category list."""
        mock_response_data = [
            {"id": "13702", "name": "General News"},
            {"id": "13703", "name": "Sector News"},
            {"id": "13704", "name": "Market News"},
            {"id": "13705", "name": "Stock Spesific News"},
        ]

        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            categories = client.news.get_news_categories(locale="en")

        path, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
        assert path == "v1/news/categories"
        assert kwargs["params"]["locale"] == "en"

        assert len(categories) == 4
        assert all(isinstance(c, NewsCategoryListItem) for c in categories)
        assert categories[0].id == "13702"
        assert categories[0].name == "General News"

    @patch("httpx.Client")
    def test_get_news_categories_without_locale(self, mock_httpx_client):
        """Locale is optional and omitted from params when not provided."""
        mock_response_data = [{"id": "13702", "name": "General News"}]

        mock_httpx_client.return_value = Mock()
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            categories = client.news.get_news_categories()

        assert "locale" not in mock_get.call_args[1]["params"]
        assert categories[0].name == "General News"

    @patch("httpx.Client")
    def test_get_news_lanes(self, mock_httpx_client):
        """Test getting the fixed news lane list."""
        mock_response_data = [
            {"id": "global_macro", "label": "Global Macro"},
            {"id": "fast_movers", "label": "Fast Movers"},
            {"id": "tr_ekonomi", "label": "TR Ekonomi"},
            {"id": "bist", "label": "Borsa İstanbul"},
        ]

        mock_httpx_client.return_value = Mock()
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            lanes = client.news.get_news_lanes()

        assert mock_get.call_args[0][0] == "v1/news/lanes"
        assert len(lanes) == 4
        assert all(isinstance(lane, NewsLaneListItem) for lane in lanes)
        assert lanes[0].id == "global_macro"
        assert lanes[0].label == "Global Macro"
        # Every returned id maps onto the NewsLane enum accepted by the filters.
        assert {lane.id for lane in lanes} == {lane.value for lane in NewsLane}

    @patch("httpx.Client")
    def test_get_news_api_source_names(self, mock_httpx_client):
        """Test getting the distinct api_source values."""
        mock_response_data = ["Reuters", "Bloomberg", "BBC", "MarketWatch"]

        mock_httpx_client.return_value = Mock()
        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data) as mock_get:
            sources = client.news.get_news_api_source_names()

        assert mock_get.call_args[0][0] == "v1/news/api-source-names"
        assert sources == ["Reuters", "Bloomberg", "BBC", "MarketWatch"]

    def test_news_client_does_not_inherit_base_client(self):
        """Test that NewsClient uses composition, not inheritance."""
        from laplace.base import BaseClient
        from laplace.news import NewsClient
        assert not issubclass(NewsClient, BaseClient)

    def test_news_stream_url_building(self):
        """Test that stream URL building works with optional filters."""
        from laplace.base import BaseClient
        from laplace.news import NewsStream
        
        mock_client = Mock(spec=BaseClient)
        mock_client.base_url = "http://test-api.com"
        
        # Test just locale and region
        stream = NewsStream(mock_client, "en", Region.US)
        url = stream._build_stream_url()
        assert "locale=en" in url
        assert "region=us" in url

        # Test all filters
        stream = NewsStream(
            mock_client,
            "tr",
            Region.TR,
            lane=NewsLane.BIST,
            sectors=["Technology", "Finance"],
            tickers=["AAPL", "MSFT"],
            categories=["Market"],
            industries=["Software"]
        )
        url = stream._build_stream_url()
        assert "locale=tr" in url
        assert "region=tr" in url
        assert "lane=bist" in url
        assert "sectors=Technology%2CFinance" in url
        assert "tickers=AAPL%2CMSFT" in url
        assert "categories=Market" in url
        assert "industries=Software" in url


class TestNewsIntegration:
    """Real integration tests (requires API key)."""

    @pytest.mark.integration
    def test_real_get_news(self, integration_client: LaplaceClient):
        """Test real API call for getting news."""
        response = integration_client.news.get_news(
            locale="tr",
            region=Region.US,
            page=0,
            page_size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert len(response.items) >= 0
        assert all(isinstance(item, News) for item in response.items)

        if response.items:
            for item in response.items:
                assert isinstance(item.created_at, datetime)
                assert item.url
                assert item.image_url is not None
                assert isinstance(item.timestamp, datetime)
                assert item.publisher.name
                assert item.quality_score >= 0

    @pytest.mark.integration
    def test_real_get_news_with_filters(self, integration_client: LaplaceClient):
        """Test real API call for getting news with filters."""
        response = integration_client.news.get_news(
            locale="tr",
            region=Region.US,
            news_type=NewsType.BLOOMBERG,
            news_order_by=NewsOrderBy.TIMESTAMP,
            direction=SortDirection.DESC,
            page=0,
            page_size=PaginationPageSize.PAGE_SIZE_10,
        )

        assert isinstance(response, PaginatedResponse)
        assert response.record_count >= 0
        assert all(isinstance(item, News) for item in response.items)

    @pytest.mark.integration
    def test_real_get_highlights(self, integration_client: LaplaceClient):
        """Test real API call for getting news highlights."""
        highlights = integration_client.news.get_highlights(
            locale="tr", region=Region.US
        )

        assert isinstance(highlights, NewsHighlight)
        assert isinstance(highlights.consumer, list)
        assert isinstance(highlights.energy_and_utilities, list)
        assert isinstance(highlights.finance, list)
        assert isinstance(highlights.healthcare, list)
        assert isinstance(highlights.industrials_and_materials, list)
        assert isinstance(highlights.tech, list)
        assert isinstance(highlights.other, list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_news_stream_connection_and_data_flow(self, integration_client: LaplaceClient):
        """Test that news stream connection works and data is flowing."""
        news_client = integration_client.news
        
        stream = await news_client.get_news_stream(locale="en", region=Region.US)
        
        events = []
        try:
            print("Testing news stream...")
            async for result in stream.receive():
                if result.error:
                    print(f"Error: {result.error}")
                    continue
                if result.data is None:
                    print("❌ FAIL: Received None data")
                    pytest.fail("Received None data from news stream")
                    
                events.append(result.data)
                print(f"Received {len(result.data)} news items")
                
                if len(events) >= 1:
                    break
        except Exception as e:
            pytest.skip(f"News streaming failed: {e}")
        finally:
            await stream.close()
            
        if events:
            assert all(isinstance(event_list, list) for event_list in events)
            
            first_event = events[0]
            if first_event:
                assert all(isinstance(item, News) for item in first_event)
                assert all(hasattr(item, "url") for item in first_event)
                assert all(hasattr(item, "created_at") for item in first_event)
            print(f"✅ News stream data flowing: {len(events)} events received")
        else:
            pytest.skip("No news events received within timeout")