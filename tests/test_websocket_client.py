"""Tests for the WebSocket client using websocket-client."""

from enum import Enum
import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from laplace import LaplaceClient
from laplace.websocket import (
    LivePriceWebSocketClient,
    LivePriceFeed,
    WebsocketOptions,
    WebSocketError,
    WebSocketErrorType,
    LogLevel,
)
from laplace.models import (
    BISTStockLiveData,
    USStockLiveData,
)


class TestWebSocketClient:
    """Test cases for the WebSocket client."""

    @pytest.fixture
    def websocket_client(self):
        """Create a WebSocket client for testing."""
        return LivePriceWebSocketClient(
            feeds=[LivePriceFeed.LIVE_BIST],
            external_user_id="test-user",
            api_key="test-api-key",
            options=WebsocketOptions(enable_logging=False),
        )

    def test_websocket_client_initialization(self, websocket_client: LivePriceWebSocketClient):
        """Test WebSocket client initialization."""
        assert websocket_client.feeds == [LivePriceFeed.LIVE_BIST]
        assert websocket_client.external_user_id == "test-user"
        assert websocket_client.api_key == "test-api-key"
        assert websocket_client._subscription_counter == 0
        assert len(websocket_client._subscriptions) == 0
        assert websocket_client._reconnect_count == 0

    def test_websocket_options_defaults(self) -> None:
        """Test WebSocket options default values."""
        options = WebsocketOptions()
        assert options.enable_logging is True
        assert options.log_level == LogLevel.ERROR
        assert options.reconnect_attempts == 5
        assert options.reconnect_delay == 5000
        assert options.max_reconnect_delay == 30000

    def test_websocket_options_custom(self) -> None:
        """Test WebSocket options with custom values."""
        options = WebsocketOptions(
            enable_logging=False,
            log_level=LogLevel.INFO,
            reconnect_attempts=3,
            reconnect_delay=1000,
            max_reconnect_delay=10000,
        )
        assert options.enable_logging is False
        assert options.log_level == LogLevel.INFO
        assert options.reconnect_attempts == 3
        assert options.reconnect_delay == 1000
        assert options.max_reconnect_delay == 10000

    def test_bist_stock_live_data(self) -> None:
        """Test BIST stock live data model."""
        data = BISTStockLiveData(
            symbol="THYAO",
            close_price=100.50,
            daily_percent_change=2.5,
            date=1234567890,
        )
        assert data.symbol == "THYAO"
        assert data.close_price == 100.50
        assert data.daily_percent_change == 2.5
        assert data.date == 1234567890

    def test_us_stock_live_data(self) -> None:
        """Test US stock live data model."""
        data = USStockLiveData(symbol="AAPL", price=150.75, date=1234567890)
        assert data.symbol == "AAPL"
        assert data.price == 150.75
        assert data.date == 1234567890

    def test_websocket_error(self) -> None:
        """Test WebSocket error creation."""
        error = WebSocketError("Test error", WebSocketErrorType.CONNECTION_ERROR)
        assert str(error) == "Test error"
        assert error.code == WebSocketErrorType.CONNECTION_ERROR
        assert error.name == "WebSocketError"

    def test_get_handlers_for_symbol_empty(
        self, websocket_client: LivePriceWebSocketClient
    ) -> None:
        """Test getting handlers for symbol when none exist."""
        handlers = websocket_client._get_handlers_for_symbol("THYAO", LivePriceFeed.LIVE_BIST)
        assert handlers == []

    def test_get_handlers_for_symbol_with_subscription(
        self, websocket_client: LivePriceWebSocketClient
    ) -> None:
        """Test getting handlers for symbol with existing subscription."""

        def mock_handler(data):
            pass

        websocket_client._subscriptions[1] = {
            "symbols": ["THYAO", "GARAN"],
            "feed": LivePriceFeed.LIVE_BIST,
            "handler": mock_handler,
        }

        handlers = websocket_client._get_handlers_for_symbol("THYAO", LivePriceFeed.LIVE_BIST)
        assert len(handlers) == 1
        assert handlers[0] == mock_handler

    def test_is_connection_closed_initial(self, websocket_client: LivePriceWebSocketClient) -> None:
        """Test initial connection closed state."""
        assert websocket_client.is_connection_closed() is False

    def test_get_close_reason_initial(self, websocket_client: LivePriceWebSocketClient) -> None:
        """Test initial close reason."""
        assert websocket_client.get_close_reason() is None

    @pytest.mark.asyncio
    async def test_connect_without_user_id_and_feeds(self) -> None:
        """Test connect without required parameters."""
        client = LivePriceWebSocketClient(feeds=[], external_user_id="", api_key="test-key")

        with pytest.raises(WebSocketError, match="External user ID and feeds are required"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_subscribe_and_unsubscribe(
        self, websocket_client: LivePriceWebSocketClient
    ) -> None:
        """Test subscription and unsubscription."""
        handler_called = False

        def mock_handler(data):
            nonlocal handler_called
            handler_called = True

        # Subscribe
        unsubscribe = websocket_client.subscribe(
            symbols=["THYAO"], feed=LivePriceFeed.LIVE_BIST, handler=mock_handler
        )

        assert len(websocket_client._subscriptions) == 1
        assert websocket_client._subscription_counter == 1

        # Unsubscribe
        unsubscribe()

        assert len(websocket_client._subscriptions) == 0

    @pytest.mark.asyncio
    async def test_handle_bist_message(self, websocket_client: LivePriceWebSocketClient) -> None:
        """Test handling BIST stock message."""
        handler_called = False
        received_data = None

        def mock_handler(data):
            nonlocal handler_called, received_data
            handler_called = True
            received_data = data

        websocket_client._subscriptions[1] = {
            "symbols": ["THYAO"],
            "feed": LivePriceFeed.LIVE_BIST,
            "handler": mock_handler,
        }

        message = json.dumps(
            {
                "type": "data",
                "feed": "live_price_tr",
                "message": {
                    "_id": 1,
                    "symbol": "THYAO",
                    "cl": 100.50,
                    "_i": "tip123",
                    "c": 2.5,
                    "d": 1234567890,
                },
            }
        )

        await websocket_client._handle_message(message)

        assert handler_called
        assert isinstance(received_data, BISTStockLiveData)
        assert received_data.symbol == "THYAO"
        assert received_data.close_price == 100.50

    @pytest.mark.asyncio
    async def test_handle_us_message(self, websocket_client):
        """Test handling US stock message."""
        handler_called = False
        received_data = None

        def mock_handler(data):
            nonlocal handler_called, received_data
            handler_called = True
            received_data = data

        websocket_client._subscriptions[1] = {
            "symbols": ["AAPL"],
            "feed": LivePriceFeed.LIVE_US,
            "handler": mock_handler,
        }

        message = json.dumps(
            {
                "type": "data",
                "feed": "live_price_us",
                "message": {"s": "AAPL", "p": 150.75, "t": 1234567890},
            }
        )

        await websocket_client._handle_message(message)

        assert handler_called
        assert isinstance(received_data, USStockLiveData)
        assert received_data.symbol == "AAPL"
        assert received_data.price == 150.75


class TestWebSocketRealIntegration:
    """Real integration tests for WebSocket client (requires API key)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_websocket_connection(self, integration_client: LaplaceClient):
        """Test real WebSocket connection and basic functionality."""
        websocket_client = integration_client.create_websocket_client(
            feeds=[LivePriceFeed.LIVE_BIST],
            external_user_id="test-integration-user",
            options=WebsocketOptions(enable_logging=False),
        )

        try:
            # Test connection
            await websocket_client.connect()

            # Test subscription
            handler_called = False
            received_data = None
            message_count = 0

            def mock_handler(data):
                nonlocal handler_called, received_data, message_count
                handler_called = True
                received_data = data
                message_count += 1
                print(f"Received data for {data.symbol}: {data}")

            unsubscribe = websocket_client.subscribe(
                symbols=["THYAO"], feed=LivePriceFeed.LIVE_BIST, handler=mock_handler
            )

            # Wait for actual data messages (longer wait for real data)
            await asyncio.sleep(10)

            # Clean up
            unsubscribe()
            await websocket_client.close()

            # Assertions about data reception
            print(f"Handler called: {handler_called}")
            print(f"Message count: {message_count}")
            print(f"Received data: {received_data}")

            # Check if we received any data
            assert handler_called, "No data was received from WebSocket"
            assert message_count > 0, f"Expected at least 1 message, got {message_count}"
            assert received_data is not None, "No data was received"
            assert isinstance(
                received_data, BISTStockLiveData
            ), f"Expected BISTStockLiveData, got {type(received_data)}"
            assert (
                received_data.symbol == "THYAO"
            ), f"Expected symbol THYAO, got {received_data.symbol}"
            assert websocket_client.is_connection_closed() is True
            assert websocket_client.get_close_reason() is not None

        except Exception as e:
            # Clean up on error
            if not websocket_client.is_connection_closed():
                await websocket_client.close()
            raise e

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_websocket_subscription_management(self, integration_client: LaplaceClient):
        """Test real WebSocket subscription management with data verification."""
        websocket_client = integration_client.create_websocket_client(
            feeds=[LivePriceFeed.LIVE_BIST, LivePriceFeed.LIVE_US],
            external_user_id="test-integration-user",
            options=WebsocketOptions(enable_logging=False),
        )

        try:
            await websocket_client.connect()

            # Test multiple subscriptions with data tracking
            received_data = {}
            message_counts = {}

            def create_handler(symbol):
                def handler(data):
                    if symbol not in received_data:
                        received_data[symbol] = []
                        message_counts[symbol] = 0
                    received_data[symbol].append(data)
                    message_counts[symbol] += 1
                    print(f"Received data for {symbol}: {data}")

                return handler

            # Subscribe to multiple symbols
            symbols = ["THYAO", "GARAN"]
            unsubscribes = []

            for symbol in symbols:
                handler = create_handler(symbol)
                unsubscribe = websocket_client.subscribe(
                    symbols=[symbol], feed=LivePriceFeed.LIVE_BIST, handler=handler
                )
                unsubscribes.append(unsubscribe)

            # Wait for data to arrive
            await asyncio.sleep(15)

            # Unsubscribe from all
            for unsubscribe in unsubscribes:
                unsubscribe()

            await websocket_client.close()

            # Verify data was received for each symbol
            print(f"Received data summary: {received_data}")
            print(f"Message counts: {message_counts}")

            # Check that we received data for at least one symbol
            total_messages = sum(message_counts.values())
            assert total_messages > 0, f"Expected at least 1 message total, got {total_messages}"

            # Verify data structure for received messages
            for symbol, data_list in received_data.items():
                assert len(data_list) > 0, f"No data received for symbol {symbol}"
                for data in data_list:
                    assert isinstance(
                        data, BISTStockLiveData
                    ), f"Expected BISTStockLiveData for {symbol}, got {type(data)}"
                    assert data.symbol == symbol, f"Expected symbol {symbol}, got {data.symbol}"
                    assert hasattr(data, "close_price"), f"Data missing close_price: {data}"
                    assert hasattr(
                        data, "daily_percent_change"
                    ), f"Data missing daily_percent_change: {data}"

            assert websocket_client.is_connection_closed() is True

        except Exception as e:
            if not websocket_client.is_connection_closed():
                await websocket_client.close()
            raise e

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_websocket_error_handling(self, integration_client: LaplaceClient):
        """Test real WebSocket error handling."""
        # Test with invalid external user ID
        websocket_client = integration_client.create_websocket_client(
            feeds=[LivePriceFeed.LIVE_BIST],
            external_user_id="",  # Invalid empty user ID
            options=WebsocketOptions(enable_logging=False),
        )

        with pytest.raises(WebSocketError, match="External user ID and feeds are required"):
            await websocket_client.connect()

        # Test with empty feeds
        websocket_client = integration_client.create_websocket_client(
            feeds=[],  # Invalid empty feeds
            external_user_id="test-user",
            options=WebsocketOptions(enable_logging=False),
        )

        with pytest.raises(WebSocketError, match="External user ID and feeds are required"):
            await websocket_client.connect()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_websocket_us_stock_data(self, integration_client: LaplaceClient):
        """Test real WebSocket US stock data reception."""
        websocket_client = integration_client.create_websocket_client(
            feeds=[LivePriceFeed.LIVE_US],
            external_user_id="test-integration-user",
            options=WebsocketOptions(enable_logging=False),
        )

        try:
            await websocket_client.connect()

            # Track received data
            received_data = []
            message_count = 0

            def mock_handler(data):
                nonlocal received_data, message_count
                received_data.append(data)
                message_count += 1
                print(f"Received US stock data: {data}")

            unsubscribe = websocket_client.subscribe(
                symbols=["AAPL", "MSFT"], feed=LivePriceFeed.LIVE_US, handler=mock_handler
            )

            # Wait for data to arrive
            await asyncio.sleep(10)

            # Clean up
            unsubscribe()
            await websocket_client.close()

            # Verify data reception
            print(f"US Stock message count: {message_count}")
            print(f"US Stock received data: {received_data}")

            # Check if we received any data
            assert message_count > 0, f"Expected at least 1 US stock message, got {message_count}"
            assert len(received_data) > 0, "No US stock data was received"

            # Verify data structure
            for data in received_data:
                assert isinstance(
                    data, USStockLiveData
                ), f"Expected USStockLiveData, got {type(data)}"
                assert data.symbol in ["AAPL", "MSFT"], f"Unexpected symbol: {data.symbol}"
                assert hasattr(data, "price"), f"Data missing price: {data}"
                assert hasattr(data, "date"), f"Data missing date: {data}"

            assert websocket_client.is_connection_closed() is True

        except Exception as e:
            if not websocket_client.is_connection_closed():
                await websocket_client.close()
            raise e
