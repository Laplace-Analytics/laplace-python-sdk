from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import (
    News,
    NewsHighlight,
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
                news_type=NewsType.Bloomberg,
                news_order_by=NewsOrderBy.Timestamp,
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
            news_type=NewsType.Bloomberg,
            news_order_by=NewsOrderBy.Timestamp,
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