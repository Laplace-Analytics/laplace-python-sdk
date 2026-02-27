"""Tests for base client functionality."""

from unittest.mock import Mock, patch

import httpx
import pytest

from laplace.base import BaseClient, LaplaceAPIError
from laplace.models import BrokerStock, BrokerStats


class TestDefaultUrls:
    """Tests for default URL configuration across clients."""

    def test_laplace_client_defaults_to_production(self):
        """Test LaplaceClient defaults to production URL, not UAT."""
        from laplace.client import LaplaceClient
        with patch("httpx.Client"):
            client = LaplaceClient(api_key="test-key")
        assert "uat" not in client.base_url
        assert client.base_url == "https://api.finfree.app/api"

    def test_websocket_client_defaults_to_production(self):
        """Test LivePriceWebSocketClient defaults to production URL, not UAT."""
        from laplace.websocket import LivePriceWebSocketClient, LivePriceFeed
        client = LivePriceWebSocketClient(
            feeds=[LivePriceFeed.LIVE_BIST],
            external_user_id="test",
            api_key="test-key",
        )
        assert "uat" not in client.base_url
        assert client.base_url == "https://api.finfree.app/api"


class TestModelConfig:
    """Tests for model_config on models that use Field aliases."""

    def test_broker_stock_populate_by_name(self):
        """Test BrokerStock can be constructed using Python field names."""
        stock = BrokerStock(
            id="1", symbol="AKBNK", name="Akbank",
            asset_type="stock", asset_class="equity",
        )
        assert stock.asset_type == "stock"
        assert stock.asset_class == "equity"

    def test_broker_stats_populate_by_name(self):
        """Test BrokerStats can be constructed using Python field names."""
        stats = BrokerStats(
            total_buy_amount=100.0, total_sell_amount=50.0,
            net_amount=50.0, total_buy_volume=1000.0,
            total_sell_volume=500.0, total_volume=1500.0,
            total_amount=150.0,
        )
        assert stats.net_amount == 50.0
        assert stats.total_volume == 1500.0


class TestBaseClient:
    """Tests for BaseClient functionality."""

    def test_init_with_default_base_url(self):
        """Test client initialization with default base URL."""
        client = BaseClient(api_key="test-key")

        assert client.api_key == "test-key"
        assert client.base_url == "https://api.finfree.app/api"

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        custom_url = "https://custom.api.com/v1"
        client = BaseClient(api_key="test-key", base_url=custom_url)

        assert client.api_key == "test-key"
        assert client.base_url == custom_url

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        client = BaseClient(api_key="test-key", base_url="https://api.test.com/")

        assert client.base_url == "https://api.test.com"

    @patch('httpx.Client')
    def test_context_manager(self, mock_httpx_client):
        """Test client can be used as context manager."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        with BaseClient(api_key="test-key") as client:
            assert client is not None

        mock_client_instance.close.assert_called_once()

    @patch('httpx.Client')
    def test_close(self, mock_httpx_client):
        """Test client close method."""
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        client.close()

        mock_client_instance.close.assert_called_once()

    @patch('httpx.Client')
    def test_successful_request(self, mock_httpx_client):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        result = client.get("test-endpoint")

        assert result == {"data": "test"}
        mock_client_instance.request.assert_called_once_with(
            method="GET",
            url="https://api.finfree.app/api/test-endpoint",
            params={"api_key": "test-key"},
            json=None
        )

    @patch('httpx.Client')
    def test_request_with_params(self, mock_httpx_client):
        """Test request with additional parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        result = client.get("test-endpoint", params={"region": "us"})

        assert result == {"data": "test"}
        mock_client_instance.request.assert_called_once_with(
            method="GET",
            url="https://api.finfree.app/api/test-endpoint",
            params={"api_key": "test-key", "region": "us"},
            json=None
        )

    @patch('httpx.Client')
    def test_http_error_handling(self, mock_httpx_client):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_response.json.return_value = {"error": "Not found"}

        http_error = httpx.HTTPStatusError("404 Not Found", request=Mock(), response=mock_response)

        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = http_error
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")

        with pytest.raises(LaplaceAPIError) as exc_info:
            client.get("test-endpoint")

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "Not found"}
        assert "404 Not Found" in str(exc_info.value)

    @patch('httpx.Client')
    def test_request_error_handling(self, mock_httpx_client):
        """Test request error handling."""
        request_error = httpx.RequestError("Connection failed")

        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = request_error
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")

        with pytest.raises(LaplaceAPIError) as exc_info:
            client.get("test-endpoint")

        assert "Connection failed" in str(exc_info.value)

    @patch('httpx.Client')
    def test_post_request(self, mock_httpx_client):
        """Test POST request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        result = client.post("test-endpoint", json={"data": "test"})

        assert result == {"created": True}
        mock_client_instance.request.assert_called_once_with(
            method="POST",
            url="https://api.finfree.app/api/test-endpoint",
            params={"api_key": "test-key"},
            json={"data": "test"}
        )

    @patch('httpx.Client')
    def test_get_bytes(self, mock_httpx_client):
        """Test get_bytes returns raw bytes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n'
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        result = client.get_bytes("test-endpoint", params={"symbol": "AKBNK"})

        assert isinstance(result, bytes)
        assert result == b'\x89PNG\r\n\x1a\n'
        mock_client_instance.request.assert_called_once_with(
            method="GET",
            url="https://api.finfree.app/api/test-endpoint",
            params={"symbol": "AKBNK", "api_key": "test-key"},
        )

    @patch('httpx.Client')
    def test_get_bytes_error_handling(self, mock_httpx_client):
        """Test get_bytes error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        mock_response.json.return_value = {"error": "Not found"}

        http_error = httpx.HTTPStatusError("404 Not Found", request=Mock(), response=mock_response)

        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = http_error
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")

        with pytest.raises(LaplaceAPIError) as exc_info:
            client.get_bytes("test-endpoint")

        assert exc_info.value.status_code == 404

    @patch('httpx.Client')
    def test_endpoint_path_handling(self, mock_httpx_client):
        """Test endpoint path handling with leading slash."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = BaseClient(api_key="test-key")
        client.get("/test-endpoint")  # Leading slash

        mock_client_instance.request.assert_called_once_with(
            method="GET",
            url="https://api.finfree.app/api/test-endpoint",
            params={"api_key": "test-key"},
            json=None
        )
