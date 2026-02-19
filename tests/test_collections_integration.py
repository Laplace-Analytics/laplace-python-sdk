"""Integration tests for collections client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from laplace import LaplaceClient
from laplace.models import Collection, CollectionDetail, CollectionStatus, CollectionStock, Region
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
    def test_get_custom_themes(self, mock_httpx_client):
        """Test getting themes."""
        mock_response_data = [
              {
                "id": "6888e18a6c84bcba9dc69ef7",
                "title": "Test Custom Theme",
                "region": [
                    "tr"
                ],
                "imageUrl": "Test Custom Theme Image URL",
                "avatarUrl": "Test Custom Theme Avatar Image",
                "numStocks": 2,
                "assetClass": "equity",
                "description": "Test Custom Theme Description",
                "image": "Test Custom Theme Image",
                "order": 0,
                "status": "active"
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            themes = client.collections.get_custom_themes(region=Region.TR, locale="en")

        assert len(themes) == 1
        assert isinstance(themes[0], Collection)
        assert themes[0].id == "6888e18a6c84bcba9dc69ef7"
        assert themes[0].title == "Test Custom Theme"
        assert themes[0].region == ["tr"]
        assert themes[0].image_url == "Test Custom Theme Image URL"
        assert themes[0].avatar_url == "Test Custom Theme Avatar Image"
        assert themes[0].num_stocks == 2
        assert themes[0].asset_class == "equity"
        assert themes[0].description == "Test Custom Theme Description"
        assert themes[0].image == "Test Custom Theme Image"
        assert themes[0].order == 0
        assert themes[0].status == "active"

    @patch("httpx.Client")
    def test_get_custom_theme_detail(self, mock_httpx_client):
        """Test getting theme detail."""
        mock_response_data = {
            "id": "67168287ca07700b58c3d305",
            "order": 1008,
            "title": "Empty to US to US+TR",
            "locale": "tr",
            "region": [
                "tr",
                "us"
            ],
            "status": "inactive",
            "stocks": [
                {
                "id": "6203d1ba1e6748752755559a",
                "name": "Apple Inc",
                "active": True,
                "symbol": "AAPL",
                "sectorId": "65533e047844ee7afe9941bf",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0972",
                "dailyChange": 0.0019939010086794094,
                "updatedDate": "2022-02-09T14:37:46.368Z"
                },
                {
                "id": "61dd0d670ec2114146342fa5",
                "name": "SASA Polyester",
                "active": True,
                "symbol": "SASA",
                "sectorId": "65533e047844ee7afe9941c0",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa097a",
                "updatedDate": "2025-08-05T14:53:59.57Z"
                }
            ],
            "imageUrl": "",
            "avatarUrl": "",
            "numStocks": 2,
            "assetClass": "equity"
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            detail = client.collections.get_custom_theme_detail(
                theme_id="67168287ca07700b58c3d305", locale="tr", region=Region.TR
            )

        assert isinstance(detail, CollectionDetail)
        assert detail.id == "67168287ca07700b58c3d305"
        assert detail.title == "Empty to US to US+TR"
        assert detail.region == ["tr", "us"]
        assert detail.status == "inactive"
        assert detail.order == 1008
        assert detail.num_stocks == 2
        assert detail.asset_class == "equity"
        assert detail.image_url == ""
        assert detail.avatar_url == ""

        # Test stocks
        assert len(detail.stocks) == 2

        apple = detail.stocks[0]
        assert apple.id == "6203d1ba1e6748752755559a"
        assert apple.name == "Apple Inc"
        assert apple.symbol == "AAPL"
        assert apple.active is True
        assert apple.asset_type == "stock"
        assert apple.sector_id == "65533e047844ee7afe9941bf"
        assert apple.industry_id == "65533e441fa5c7b58afa0972"
        assert apple.daily_change == 0.0019939010086794094
        assert isinstance(apple.updated_date, datetime)

        sasa = detail.stocks[1]
        assert sasa.id == "61dd0d670ec2114146342fa5"
        assert sasa.name == "SASA Polyester"
        assert sasa.symbol == "SASA"
        assert sasa.active is True
        assert sasa.daily_change is None
        assert isinstance(sasa.updated_date, datetime)

    @patch("httpx.Client")
    def test_get_industries(self, mock_httpx_client):
        """Test getting industries."""
        mock_response_data = [          
            {
                "id": "65533e441fa5c7b58afa0944",
                "title": "Perakende (Özel Hatlar)",
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ecommerce-stocks_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ecommerce-stocks_avatar.webp",
                "numStocks": 2
            },
            {
                "id": "65533e441fa5c7b58afa0975",
                "title": "Yarı İletken",
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/donanim_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/donanim_avatar.webp",
                "numStocks": 3
            },
            {
                "id": "65533e441fa5c7b58afa092b",
                "title": "Reklamcılık",
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/advertising-agencies_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/advertising-agencies_avatar.webp",
                "numStocks": 2
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            industries = client.collections.get_industries(region=Region.TR)

        assert len(industries) == 3
        assert isinstance(industries[0], Collection)
        assert industries[0].id == "65533e441fa5c7b58afa0944"
        assert industries[0].title == "Perakende (Özel Hatlar)"
        assert industries[0].num_stocks == 2
        assert industries[0].image_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ecommerce-stocks_original.webp"
        assert industries[0].avatar_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ecommerce-stocks_avatar.webp"

    @patch("httpx.Client")
    def test_get_industry_detail(self, mock_httpx_client):
        """Test getting industry detail."""
        mock_response_data = {
            "id": "65533e441fa5c7b58afa0944",
            "order": 0,
            "title": "Perakende (Özel Hatlar)",
            "region": [
                "us",
                "tr"
            ],
            "stocks": [
                {
                "id": "61dd0d850ec2114146343053",
                "name": "Teknosa",
                "active": True,
                "symbol": "TKNSA",
                "sectorId": "65533e047844ee7afe9941b9",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0944",
                "updatedDate": "2025-07-02T00:00:00.426Z"
                },
                {
                "id": "6261a8fd0e45cb0010dcbe14",
                "name": "Suwen Tekstil",
                "active": True,
                "symbol": "SUWEN",
                "sectorId": "65533e047844ee7afe9941b9",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0944",
                "updatedDate": "2022-04-21T18:56:59.898Z"
                }
            ],
            "imageUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/retail-special-lines.webp",
            "avatarUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/retail-special-lines_avatar.webp",
            "numStocks": 59
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        industry_id = "65533e441fa5c7b58afa0944"
        
        with patch.object(client, "get", return_value=mock_response_data):
            detail = client.collections.get_industry_detail(industry_id=industry_id, region=Region.TR)

        assert isinstance(detail, CollectionDetail)
        assert detail.id == industry_id
        assert detail.title == "Perakende (Özel Hatlar)"
        assert detail.order == 0
        assert detail.num_stocks == 59
        assert "tr" in detail.region
        assert detail.image_url == "https://finfree-storage.s3.amazonaws.com/collection-images/retail-special-lines.webp"
        assert detail.avatar_url == "https://finfree-storage.s3.amazonaws.com/collection-images/retail-special-lines_avatar.webp"

        assert len(detail.stocks) == 2

        first_stock = detail.stocks[0]
        assert first_stock.id == "61dd0d850ec2114146343053"
        assert first_stock.name == "Teknosa"
        assert first_stock.active is True
        assert first_stock.symbol == "TKNSA"
        assert first_stock.sector_id == "65533e047844ee7afe9941b9"
        assert first_stock.asset_type == "stock"
        assert first_stock.industry_id == industry_id
        assert isinstance(first_stock.updated_date, datetime)

        assert detail.stocks[1].symbol == "SUWEN"
        assert detail.stocks[1].name == "Suwen Tekstil"

    @patch("httpx.Client")
    def test_get_sectors(self, mock_httpx_client):
        """Test getting sectors."""
        mock_response_data = [
            {
                "id": "65533e047844ee7afe9941b9",
                "title": "Tüketici Döngüsel",
                "imageUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical.webp",
                "avatarUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical_avatar.webp",
                "numStocks": 87
            },
            {
                "id": "65533e047844ee7afe9941ba",
                "title": "Tüketici Defansif",
                "imageUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-defensive.webp",
                "avatarUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-defensive_avatar.webp",
                "numStocks": 68
            },
            {
                "id": "65533e047844ee7afe9941bf",
                "title": "Teknoloji",
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/informationtechnology-stocks_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/informationtechnology-stocks_avatar.webp",
                "numStocks": 42
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            sectors = client.collections.get_sectors(region=Region.TR)

        assert len(sectors) == 3
        assert isinstance(sectors[0], Collection)
        assert sectors[0].id == "65533e047844ee7afe9941b9"
        assert sectors[0].title == "Tüketici Döngüsel"
        assert sectors[0].num_stocks == 87
        assert sectors[0].image_url == "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical.webp"
        assert sectors[0].avatar_url == "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical_avatar.webp"


    @patch("httpx.Client")
    def test_get_sector_detail(self, mock_httpx_client):
        """Test getting sector detail."""
        mock_response_data = {
            "id": "65533e047844ee7afe9941b9",
            "order": 0,
            "title": "Tüketici Döngüsel",
            "region": [
                "us",
                "tr"
            ],
            "stocks": [
                {
                "id": "61dd0d430ec2114146342f2e",
                "name": "Bosch Fren Sistemleri",
                "active": True,
                "symbol": "BFREN",
                "sectorId": "65533e047844ee7afe9941b9",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0935",
                "updatedDate": "2022-01-11T04:53:23.155Z"
                }
            ],
            "imageUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical.webp",
            "avatarUrl": "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical_avatar.webp",
            "numStocks": 797
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        sector_id = "65533e047844ee7afe9941b9"

        with patch.object(client, "get", return_value=mock_response_data):
            detail = client.collections.get_sector_detail(sector_id=sector_id, region=Region.TR)

        assert isinstance(detail, Collection)
        assert detail.id == "65533e047844ee7afe9941b9"
        assert detail.order == 0
        assert detail.title == "Tüketici Döngüsel"
        assert isinstance(detail.region, list)
        assert "us" in detail.region
        assert "tr" in detail.region
        assert detail.image_url == "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical.webp"
        assert detail.avatar_url == "https://finfree-storage.s3.amazonaws.com/collection-images/consumer-cyclical_avatar.webp"
        assert detail.num_stocks == 797

        assert len(detail.stocks) == 1
        stock = detail.stocks[0]
        
        assert stock.id == "61dd0d430ec2114146342f2e"
        assert stock.name == "Bosch Fren Sistemleri"
        assert stock.active is True
        assert stock.symbol == "BFREN"
        assert stock.sector_id == "65533e047844ee7afe9941b9"
        assert stock.asset_type == "stock"
        assert stock.industry_id == "65533e441fa5c7b58afa0935"
        assert isinstance(stock.updated_date, datetime)

    @patch("httpx.Client")
    def test_get_themes(self, mock_httpx_client):
        """Test getting themes."""
        mock_response_data = [
            {
                "id": "6256b37b53c18400117a8598",
                "title": "Temettü Aristokratları",
                "region": [
                    "tr"
                ],
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/temettu-padisahlari_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/temettu-padisahlari_avatar.webp",
                "numStocks": 12,
                "assetClass": "equity"
            },
            {
                "id": "6256b0647d0bb100123effa7",
                "title": "İhracat Şampiyonları",
                "region": [
                    "tr"
                ],
                "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_original.webp",
                "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_avatar.webp",
                "numStocks": 15,
                "assetClass": "equity"
            }
        ]

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        with patch.object(client, "get", return_value=mock_response_data):
            themes = client.collections.get_custom_themes(locale="tr", region=Region.TR)

        assert len(themes) == 2
        assert isinstance(themes[0], Collection)
        assert themes[0].id == "6256b37b53c18400117a8598"
        assert themes[0].title == "Temettü Aristokratları"
        assert "tr" in themes[0].region
        assert themes[0].image_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/temettu-padisahlari_original.webp"
        assert themes[0].avatar_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/temettu-padisahlari_avatar.webp"
        assert themes[0].num_stocks == 12
        assert themes[0].asset_class == "equity"


    @patch("httpx.Client")
    def test_get_theme_detail(self, mock_httpx_client):
        """Test getting theme detail."""
        mock_response_data = {
            "id": "6256b0647d0bb100123effa7",
            "image": "https://finfree-storage.s3.eu-central-1.amazonaws.com/themes/tr/ihracat_sampiyonlari.png",
            "order": 0,
            "title": "İhracat Şampiyonları",
            "region": [
                "tr"
            ],
            "stocks": [
                {
                "id": "61dd0d4b0ec2114146342f69",
                "name": "Şişe ve Cam Fabrikaları",
                "active": True,
                "symbol": "SISE",
                "sectorId": "65533e047844ee7afe9941be",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0956",
                "updatedDate": "2025-09-16T09:55:43.644Z"
                },
                {
                "id": "61dd0d820ec211414634303e",
                "name": "Vestel Elektronik",
                "active": True,
                "symbol": "VESTL",
                "sectorId": "65533e047844ee7afe9941b9",
                "assetType": "stock",
                "industryId": "65533e441fa5c7b58afa0939",
                "updatedDate": "2025-09-16T09:55:43.644Z"
                }
            ],
            "imageUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_original.webp",
            "avatarUrl": "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_avatar.webp",
            "numStocks": 15,
            "assetClass": "equity"
        }

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = MockResponse(mock_response_data)
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")

        theme_id = "6256b0647d0bb100123effa7"

        with patch.object(client, "get", return_value=mock_response_data):
            detail = client.collections.get_custom_theme_detail(
                theme_id=theme_id, locale="tr", region=Region.TR
            )

        assert isinstance(detail, CollectionDetail)
        assert detail.id == theme_id
        assert detail.title == "İhracat Şampiyonları"
        assert detail.image == "https://finfree-storage.s3.eu-central-1.amazonaws.com/themes/tr/ihracat_sampiyonlari.png"
        assert detail.order == 0
        assert "tr" in detail.region
        assert detail.image_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_original.webp"
        assert detail.avatar_url == "https://finfree-storage.s3.eu-central-1.amazonaws.com/collection-images/ihracat-sampiyonlari_avatar.webp"
        assert detail.num_stocks == 15
        assert detail.asset_class == "equity"

        assert len(detail.stocks) == 2

        sise = detail.stocks[0]
        assert sise.id == "61dd0d4b0ec2114146342f69"
        assert sise.name == "Şişe ve Cam Fabrikaları"
        assert sise.active is True
        assert sise.symbol == "SISE"
        assert sise.sector_id == "65533e047844ee7afe9941be"
        assert sise.asset_type == "stock"
        assert sise.industry_id == "65533e441fa5c7b58afa0956"
        assert isinstance(sise.updated_date, datetime)

    @patch("httpx.Client")
    def test_create_custom_theme(self, mock_httpx_client):
        """Test creating a custom theme sends correct request."""
        mock_response_data = {"id": "64abc123def4567890123456"}

        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        mock_post = Mock(return_value=mock_response_data)

        with patch.object(client, "post", mock_post):
            theme_id = client.collections.create_custom_theme(
                title={"tr": "Test Tema", "en": "Test Theme"},
                stock_ids=["61dd0d670ec2114146342fa5", "61dd0d7a0ec2114146343014"],
                status=CollectionStatus.ACTIVE,
                description={"tr": "Açıklama", "en": "Description"},
                image_url="https://example.com/image.jpg",
            )

        assert isinstance(theme_id, str)
        assert theme_id == "64abc123def4567890123456"

        mock_post.assert_called_once_with(
            "v1/custom-theme",
            json={
                "title": {"tr": "Test Tema", "en": "Test Theme"},
                "stocks": ["61dd0d670ec2114146342fa5", "61dd0d7a0ec2114146343014"],
                "status": "active",
                "description": {"tr": "Açıklama", "en": "Description"},
                "image_url": "https://example.com/image.jpg",
            },
        )

    @patch("httpx.Client")
    def test_update_custom_theme(self, mock_httpx_client):
        """Test updating a custom theme sends correct request."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        mock_patch = Mock(return_value=None)

        with patch.object(client, "patch", mock_patch):
            client.collections.update_custom_theme(
                theme_id="64abc123def4567890123456",
                title={"tr": "Güncel Tema", "en": "Updated Theme"},
                stock_ids=["stock1", "stock2"],
                status=CollectionStatus.INACTIVE,
                description={"tr": "Açıklama", "en": "Description"},
                image_url="https://example.com/image.jpg",
                image="base64data",
                avatar_url="https://example.com/avatar.jpg",
                meta_data={"color": "#FF0000"},
            )

        mock_patch.assert_called_once_with(
            "v1/custom-theme/64abc123def4567890123456",
            json={
                "title": {"tr": "Güncel Tema", "en": "Updated Theme"},
                "stockIds": ["stock1", "stock2"],
                "status": "inactive",
                "description": {"tr": "Açıklama", "en": "Description"},
                "image_url": "https://example.com/image.jpg",
                "image": "base64data",
                "avatar_url": "https://example.com/avatar.jpg",
                "meta_data": {"color": "#FF0000"},
            },
        )

    @patch("httpx.Client")
    def test_delete_custom_theme(self, mock_httpx_client):
        """Test deleting a custom theme sends correct request."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = LaplaceClient(api_key="test-key")
        mock_delete = Mock(return_value=None)

        with patch.object(client, "delete", mock_delete):
            client.collections.delete_custom_theme(theme_id="64abc123def4567890123456")

        mock_delete.assert_called_once_with("v1/custom-theme/64abc123def4567890123456")

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


    @pytest.mark.integration
    def test_real_get_themes(self, integration_client: LaplaceClient):
        """Test real API call for getting themes."""
        themes = integration_client.collections.get_themes(region=Region.TR)

        assert len(themes) > 0
        
        t = themes[0]
        
        assert isinstance(t, Collection)
        assert t.id and t.title
        assert t.image_url is not None
        assert t.avatar_url is not None
        assert isinstance(t.num_stocks, int)

    @pytest.mark.integration
    def test_real_get_theme_detail(self, integration_client: LaplaceClient):
        """Test real API call for getting theme detail."""
        themes = integration_client.collections.get_themes(region=Region.TR)
        assert len(themes) > 0

        detail = integration_client.collections.get_theme_detail(
            theme_id=themes[0].id, region=Region.TR
        )

        assert isinstance(detail, CollectionDetail)
        assert detail.id == themes[0].id
        
        if detail.stocks:
            s = detail.stocks[0]
            assert isinstance(s, CollectionStock)
            assert s.id and s.symbol
            assert s.asset_type == "stock"
            assert s.name
            assert s.active is not None
            assert s.sector_id is not None
            assert s.industry_id is not None
            assert isinstance(s.updated_date, datetime) 

    @pytest.mark.integration
    def test_real_get_industries(self, integration_client: LaplaceClient):
        """Test real API call for getting industries."""
        industries = integration_client.collections.get_industries(region=Region.TR)
        assert len(industries) > 0
        
        i = industries[0]
        assert isinstance(i, Collection)
        assert i.id and i.title
        assert i.avatar_url is not None
        assert isinstance(i.num_stocks, int)
        assert i.image_url is not None

    @pytest.mark.integration
    def test_real_get_industry_detail(self, integration_client: LaplaceClient):
        """Test real API call for getting industry detail."""
        industries = integration_client.collections.get_industries(region=Region.TR)
        assert len(industries) > 0

        detail = integration_client.collections.get_industry_detail(
            industry_id=industries[0].id, region=Region.TR
        )

        if detail.stocks:
            s = detail.stocks[0]
            assert isinstance(s, CollectionStock)
            assert s.id and s.symbol
            assert s.asset_type == "stock"
            assert s.name
            assert s.active is not None
            assert s.sector_id is not None
            assert s.industry_id is not None
            assert isinstance(s.updated_date, datetime) 

    @pytest.mark.integration
    def test_real_get_sectors(self, integration_client: LaplaceClient):
        """Test real API call for getting sectors."""
        sectors = integration_client.collections.get_sectors(region=Region.TR)

        s = sectors[0]
        assert isinstance(s, Collection)
        assert s.id and s.title
        assert s.avatar_url is not None
        assert isinstance(s.num_stocks, int)
        assert s.image_url is not None

    @pytest.mark.integration
    def test_real_get_sector_detail(self, integration_client: LaplaceClient):
        """Test real API call for getting sector detail."""
        sectors = integration_client.collections.get_sectors(region=Region.TR)
        assert len(sectors) > 0

        detail = integration_client.collections.get_sector_detail(
            sector_id=sectors[0].id, region=Region.TR
        )

        if detail.stocks:
            s = detail.stocks[0]
            assert isinstance(s, CollectionStock)
            assert s.id and s.symbol
            assert s.asset_type == "stock"
            assert s.name
            assert s.active is not None
            assert s.sector_id is not None
            assert s.industry_id is not None
            assert isinstance(s.updated_date, datetime) 

    @pytest.mark.integration
    def test_real_get_custom_themes(self, integration_client: LaplaceClient):
        """Test real API call for getting custom themes."""
        themes = integration_client.collections.get_custom_themes(
            locale="tr", region=Region.TR
        )

        assert isinstance(themes, list)
        assert all(isinstance(t, Collection) for t in themes)

        t = themes[0]
        assert isinstance(t, Collection)
        assert t.id and t.title
        assert t.avatar_url is not None
        assert isinstance(t.num_stocks, int)
        assert t.image_url is not None
        assert t.asset_class == "equity"
        assert t.status is not None
        if t.region:
            assert "tr" in t.region

    @pytest.mark.integration
    def test_real_create_update_delete_custom_theme(self, integration_client: LaplaceClient):
        """Test real API flow: create, update, then delete a custom theme."""
        # Create
        theme_id = integration_client.collections.create_custom_theme(
            title={"tr": "Test Tema", "en": "Test Theme"},
            stock_ids=[],
            status=CollectionStatus.ACTIVE,
        )
        assert isinstance(theme_id, str)
        assert len(theme_id) > 0

        # Update
        integration_client.collections.update_custom_theme(
            theme_id=theme_id,
            title={"tr": "Güncel Tema", "en": "Updated Theme"},
            status=CollectionStatus.INACTIVE,
        )

        # Delete
        integration_client.collections.delete_custom_theme(theme_id=theme_id)
