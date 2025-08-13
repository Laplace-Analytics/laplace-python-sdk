"""WebSocket client for Laplace live price data."""

import asyncio
from enum import Enum
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union
import threading

from pydantic import BaseModel
from websocket import WebSocketApp, WebSocketConnectionClosedException

from .base import BaseClient, LaplaceError
from .models import (
    BISTStockLiveData,
    BISTStockOrderBookData,
    USStockLiveData,
)


class AccessorType(str, Enum):
    """Accessor type for user details."""

    USER = "user"


class LivePriceFeed(str, Enum):
    """Live price feed types."""

    LIVE_BIST = "live_price_tr"
    LIVE_US = "live_price_us"
    DELAYED_BIST = "delayed_price_tr"
    DEPTH_BIST = "depth_tr"


class LogLevel(str, Enum):
    """Log level options."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class WebSocketErrorType(str, Enum):
    """WebSocket error types."""

    MAX_RECONNECT_EXCEEDED = "MAX_RECONNECT_EXCEEDED"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CLOSE_ERROR = "CLOSE_ERROR"
    WEBSOCKET_NOT_INITIALIZED = "WEBSOCKET_NOT_INITIALIZED"
    MESSAGE_PARSE_ERROR = "MESSAGE_PARSE_ERROR"
    WEBSOCKET_NOT_CONNECTED = "WEBSOCKET_NOT_CONNECTED"
    WEBSOCKET_ERROR = "WEBSOCKET_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class WebSocketCloseReason(str, Enum):
    """WebSocket close reasons."""

    NORMAL_CLOSURE = "NORMAL_CLOSURE"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    MAX_RECONNECT_EXCEEDED = "MAX_RECONNECT_EXCEEDED"
    UNKNOWN = "UNKNOWN"


class WebsocketOptions(BaseModel):
    """WebSocket options."""

    enable_logging: bool = True
    log_level: LogLevel = LogLevel.ERROR
    reconnect_attempts: int = 5
    reconnect_delay: int = 5000
    max_reconnect_delay: int = 30000


class WebSocketError(LaplaceError):
    """WebSocket specific error."""

    def __init__(self, message: str, code: WebSocketErrorType = WebSocketErrorType.UNKNOWN_ERROR):
        super().__init__(message)
        self.code = code
        self.name = "WebSocketError"


class LivePriceWebSocketClient(BaseClient):
    """WebSocket client for live price data using websocket-client."""

    def __init__(
        self,
        feeds: List[LivePriceFeed],
        external_user_id: str,
        api_key: str,
        base_url: str = "https://uat.api.finfree.app/api",
        options: Optional[WebsocketOptions] = None,
    ):
        """Initialize the WebSocket client.

        Args:
            feeds: List of feeds to subscribe to
            external_user_id: External user ID
            api_key: Laplace API key
            base_url: Base URL for the API
            options: WebSocket configuration options
        """
        super().__init__(api_key, base_url)

        self.feeds = feeds
        self.external_user_id = external_user_id
        self._options = options or WebsocketOptions()

        # WebSocket state
        self._websocket: Optional[WebSocketApp] = None
        self._subscription_counter = 0
        self._subscriptions: Dict[int, Dict[str, Any]] = {}
        self._symbol_last_data: Dict[str, Union[BISTStockLiveData, USStockLiveData]] = {}
        self._is_closed = False
        self._closed_reason: Optional[WebSocketCloseReason] = None
        self._ws_url: Optional[str] = None
        self._connection_thread: Optional[threading.Thread] = None
        self._reconnect_count = 0
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        # Setup logging
        self._logger = logging.getLogger(__name__)
        if self._options.enable_logging:
            self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[LivePriceWebSocket][%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        if self._options.log_level == LogLevel.ERROR:
            self._logger.setLevel(logging.ERROR)
        elif self._options.log_level == LogLevel.WARN:
            self._logger.setLevel(logging.WARNING)
        else:
            self._logger.setLevel(logging.INFO)

    def _log(self, message: str, level: str = "info"):
        """Log a message with the specified level."""
        if not self._options.enable_logging:
            return

        if level == "error":
            self._logger.error(message)
        elif level == "warn":
            self._logger.warning(message)
        else:
            self._logger.info(message)

    async def update_user_details(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country_code: Optional[str] = None,
        accessor_type: Optional[AccessorType] = None,
        active: bool = True,
    ) -> None:
        """Update user details.

        Args:
            params: User details parameters
        """
        url = f"{self.base_url}/api/v1/ws/user"

        data = {
            "externalUserID": self.external_user_id,
            "active": active,
        }

        if first_name:
            data["firstName"] = first_name
        if last_name:
            data["lastName"] = last_name
        if address:
            data["address"] = address
        if city:
            data["city"] = city
        if country_code:
            data["countryCode"] = country_code
        if accessor_type:
            data["accessorType"] = accessor_type.value

        await self._async_request("PUT", url, json=data)

    async def _get_websocket_url(self) -> str:
        """Get WebSocket URL from the API.

        Returns:
            WebSocket URL
        """
        url = f"{self.base_url}/v2/ws/url"

        feeds = [feed.value for feed in self.feeds]

        response = await self._async_request(
            "POST",
            url,
            json={
                "externalUserId": self.external_user_id,
                "feeds": feeds,
            },
        )

        return response["url"]

    async def _async_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make an async HTTP request."""
        import httpx

        # Add API key to params if not already present
        params = kwargs.get("params", {})
        if "api_key" not in params:
            params["api_key"] = self.api_key
            kwargs["params"] = params

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Log the error response for debugging
                try:
                    error_data = e.response.json()
                    self._log(f"HTTP Error Response: {error_data}", "error")
                except:
                    self._log(f"HTTP Error Response: {e.response.text}", "error")
                raise

    async def connect(self, url: Optional[str] = None) -> None:
        """Connect to the WebSocket with automatic reconnection.

        Args:
            url: Optional WebSocket URL (if not provided, will be fetched from API)
        """
        self._log("Connecting to WebSocket...")

        if not self.external_user_id or not self.feeds:
            raise WebSocketError("External user ID and feeds are required")

        # Store the current event loop
        self._loop = asyncio.get_running_loop()

        if url:
            self._ws_url = url
        else:
            self._ws_url = await self._get_websocket_url()

        # Create WebSocket with automatic reconnection
        self._websocket = WebSocketApp(
            self._ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        # Start WebSocket in a separate thread
        if not self._connection_thread or not self._connection_thread.is_alive():
            self._connection_thread = threading.Thread(
                target=self._websocket.run_forever, daemon=True
            )
            self._connection_thread.start()

    def _on_open(self, ws):
        """Called when WebSocket connection is opened."""
        self._log("WebSocket connected")
        self._reconnect_count = 0
        # Resubscribe to all symbols using run_coroutine_threadsafe
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._resubscribe_all(), self._loop)

    def _on_message(self, ws, message):
        """Called when a message is received."""
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._handle_message(message), self._loop)

    def _on_error(self, ws, error):
        """Called when a WebSocket error occurs."""
        self._log(f"WebSocket error: {error}", "error")

    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection is closed."""
        self._log(f"WebSocket closed: {close_status_code} - {close_msg}")

        if not self._is_closed:
            self._reconnect_count += 1
            if self._reconnect_count >= self._options.reconnect_attempts:
                self._closed_reason = WebSocketCloseReason.MAX_RECONNECT_EXCEEDED
                self._log(
                    f"Maximum reconnection attempts ({self._options.reconnect_attempts}) reached",
                    "error",
                )
            else:
                self._log(
                    f"Reconnecting... (attempt {self._reconnect_count}/{self._options.reconnect_attempts})"
                )

    async def _resubscribe_all(self) -> None:
        """Resubscribe to all symbols after reconnection."""
        symbols_by_feed: Dict[LivePriceFeed, List[str]] = {}
        for subscription in self._subscriptions.values():
            symbols = subscription["symbols"]
            feed = subscription["feed"]
            if feed not in symbols_by_feed:
                symbols_by_feed[feed] = []
            for symbol in symbols:
                if symbol not in symbols_by_feed[feed]:
                    symbols_by_feed[feed].append(symbol)

        for feed, symbols in symbols_by_feed.items():
            await self._add_symbols(symbols, feed)

    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            raw_data = json.loads(message)
            feed = LivePriceFeed(raw_data.get("feed"))
            message_type = raw_data.get("type")

            if message_type == "data":
                message_data = raw_data.get("message")
                if not message_data:
                    raise WebSocketError(
                        "Price update message is empty", WebSocketErrorType.MESSAGE_PARSE_ERROR
                    )

                if feed == LivePriceFeed.DELAYED_BIST or feed == LivePriceFeed.LIVE_BIST:
                    price_data = BISTStockLiveData(
                        symbol=message_data.get("symbol"),
                        close_price=message_data.get("cl"),
                        daily_percent_change=message_data.get("c"),
                        date=message_data.get("d"),
                    )
                elif feed == LivePriceFeed.LIVE_US:
                    price_data = USStockLiveData(
                        symbol=message_data.get("s"),
                        price=message_data.get("p"),
                        date=message_data.get("t"),
                    )
                elif feed == LivePriceFeed.DEPTH_BIST:
                    price_data = BISTStockOrderBookData(
                        symbol=message_data.get("s"),
                        updated=message_data.get("updated"),
                        deleted=message_data.get("deleted"),
                    )

                if price_data.symbol:
                    self._symbol_last_data[price_data.symbol] = price_data
                    handlers = self._get_handlers_for_symbol(price_data.symbol, feed)
                    for handler in handlers:
                        handler(price_data)

            elif message_type == "heartbeat":
                self._log("Received heartbeat")

            elif message_type == "error":
                self._log(f"Received error: {raw_data.get('message')}", "error")

            elif message_type == "warning":
                self._log(f"Received warning: {raw_data.get('message')}", "warn")

            else:
                self._log(f"Unknown message type: {message_type}", "error")

        except json.JSONDecodeError as e:
            self._log(f"Failed to parse WebSocket message: {e}", "error")
        except Exception as e:
            self._log(f"Error handling message: {e}", "error")

    def subscribe(
        self,
        symbols: List[str],
        feed: LivePriceFeed,
        handler: Callable[[Union[BISTStockLiveData, USStockLiveData]], None],
    ) -> Callable[[], None]:
        """Subscribe to symbols for a specific feed.

        Args:
            symbols: List of symbols to subscribe to
            feed: Feed type to subscribe to
            handler: Callback function for price updates

        Returns:
            Unsubscribe function
        """
        subscription_id = self._subscription_counter
        self._subscription_counter += 1

        symbols_to_add = []

        self._subscriptions[subscription_id] = {
            "symbols": symbols,
            "feed": feed,
            "handler": handler,
        }

        for symbol in symbols:
            symbol_handlers = self._get_handlers_for_symbol(symbol, feed)
            if len(symbol_handlers) == 1:
                symbols_to_add.append(symbol)
            elif len(symbol_handlers) > 1:
                last_data = self._symbol_last_data.get(symbol)
                if last_data:
                    handler(last_data)

        if symbols_to_add:
            if self._loop:
                asyncio.run_coroutine_threadsafe(
                    self._add_symbols(symbols_to_add, feed), self._loop
                )

        def unsubscribe():
            """Unsubscribe from the symbols."""
            if subscription_id in self._subscriptions:
                del self._subscriptions[subscription_id]

                symbols_for_remove = []
                for symbol in symbols:
                    if len(self._get_handlers_for_symbol(symbol, feed)) == 0:
                        symbols_for_remove.append(symbol)

                if symbols_for_remove:
                    if self._loop:
                        asyncio.run_coroutine_threadsafe(
                            self._remove_symbols(symbols_for_remove, feed), self._loop
                        )

        return unsubscribe

    def _get_handlers_for_symbol(
        self, symbol: str, feed: LivePriceFeed
    ) -> List[Callable[[Union[BISTStockLiveData, USStockLiveData]], None]]:
        """Get all handlers for a specific symbol and feed."""
        handlers = []
        for subscription in self._subscriptions.values():
            if symbol in subscription["symbols"] and subscription["feed"] == feed:
                handlers.append(subscription["handler"])
        return handlers

    async def _add_symbols(self, symbols: List[str], feed: LivePriceFeed) -> None:
        """Add symbols to subscription."""
        if not symbols or not self._websocket:
            return

        message = {
            "type": "subscribe",
            "symbols": symbols,
            "feed": feed.value,
        }

        try:
            self._websocket.send(json.dumps(message))
        except WebSocketConnectionClosedException:
            self._log("WebSocket not connected, message will be sent on reconnection", "warn")

    async def _remove_symbols(self, symbols: List[str], feed: LivePriceFeed) -> None:
        """Remove symbols from subscription."""
        if not symbols or not self._websocket:
            return

        message = {
            "type": "unsubscribe",
            "symbols": symbols,
            "feed": feed.value,
        }

        try:
            self._websocket.send(json.dumps(message))
        except WebSocketConnectionClosedException:
            self._log("WebSocket not connected, message will be sent on reconnection", "warn")

    async def close(self) -> None:
        """Close the WebSocket connection."""
        try:
            self._subscriptions.clear()
            self._closed_reason = WebSocketCloseReason.NORMAL_CLOSURE
            self._is_closed = True

            if self._websocket:
                self._websocket.close()

            if self._connection_thread and self._connection_thread.is_alive():
                self._connection_thread.join(timeout=5)

        except Exception as e:
            error_message = f"Unexpected error during close: {e}"
            self._log(error_message, "error")
            raise WebSocketError(error_message, WebSocketErrorType.CLOSE_ERROR)

        finally:
            self._websocket = None
            self._subscriptions.clear()

    def is_connection_closed(self) -> bool:
        """Check if the connection is closed.

        Returns:
            True if connection is closed, False otherwise
        """
        return self._is_closed

    def get_close_reason(self) -> Optional[WebSocketCloseReason]:
        """Get the reason for connection closure.

        Returns:
            Close reason or None if not closed
        """
        return self._closed_reason
