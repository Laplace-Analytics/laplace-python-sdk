"""Live price streaming functionality for Laplace API."""

import asyncio
import json
import uuid
from enum import Enum
from typing import AsyncGenerator, Generic, Optional, List
import httpx
from pydantic import BaseModel
from laplace.models import (
    T,
    BISTStockOrderBookData,
    LiveMessageV2,
    Region,
    BISTStockLiveData,
    USStockLiveData,
    BISTBidAskData,
)
from laplace.base import BaseClient
BidAskData = BISTBidAskData

class LivePriceType(Enum):
    """Live price type."""

    PRICE = "price"
    DELAYED_PRICE = "delayed-price"
    ORDER_BOOK = "order-book"


class LivePriceResult(BaseModel, Generic[T]):
    """Result wrapper for live price data."""

    data: Optional[T] = None
    error: Optional[str] = None

    @property
    def is_error(self) -> bool:
        return self.error is not None


class BidAskResult:
    """Result wrapper for bid/ask price data."""

    def __init__(self, data: Optional[BidAskData] = None, error: Optional[str] = None):
        self.data = data
        self.error = error

    @property
    def is_error(self) -> bool:
        return self.error is not None


class LivePriceStream(Generic[T]):
    """Handles live price streaming for a specific region."""

    def __init__(self, base_client: BaseClient, type: LivePriceType, region: Region):
        self.base_client = base_client
        self.region = region
        self.type = type
        self._task: Optional[asyncio.Task] = None
        self._queue: Optional[asyncio.Queue[LivePriceResult[T]]] = None
        self._is_closed = False
        self._symbols: List[str] = []

    async def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to live price updates for given symbols."""
        await self._cleanup_existing_stream()

        self._symbols = symbols
        self._queue = asyncio.Queue[LivePriceResult[T]]()
        self._is_closed = False
        self._task = asyncio.create_task(self._start_streaming())

    async def receive(self) -> AsyncGenerator[LivePriceResult[T], None]:
        """Receive live price data from the stream."""
        if not self._queue:
            raise RuntimeError("Not subscribed. Call subscribe() first.")

        while not self._is_closed:
            try:
                result = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield result
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def close(self) -> None:
        """Close the stream and cleanup resources."""
        if self._is_closed:
            return

        self._is_closed = True
        await self._cleanup_existing_stream()

    async def _cleanup_existing_stream(self) -> None:
        """Cancel and cleanup existing streaming task."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def _build_stream_url(self) -> str:
        """Build the streaming URL for the given symbols and region."""
        stream_id = str(uuid.uuid4())
        symbols_param = ",".join(self._symbols) if self._symbols else ""

        url = self.base_client.base_url
        if self.type == LivePriceType.PRICE and self.region == Region.TR:
            url = f"{url}/v2/stock/price/live"
        elif self.type == LivePriceType.DELAYED_PRICE:
            url = f"{url}/v1/stock/price/delayed"
        elif self.type == LivePriceType.ORDER_BOOK:
            url = f"{url}/v1/stock/orderbook/live"

        return f"{url}?filter={symbols_param}&region={self.region.value}&stream={stream_id}"

    def _create_model_from_data(self, data: dict) -> T:
        """Create appropriate data model based on region."""
        if self.region == Region.TR and self.type == LivePriceType.PRICE:
            return LiveMessageV2[BISTStockLiveData](**data)  # type: ignore
        elif self.region == Region.TR and self.type == LivePriceType.DELAYED_PRICE:
            return LiveMessageV2[BISTStockLiveData](**data)  # type: ignore
        elif self.region == Region.US and self.type == LivePriceType.PRICE:
            return USStockLiveData(**data)  # type: ignore
        elif self.region == Region.TR and self.type == LivePriceType.ORDER_BOOK:
            return BISTStockOrderBookData(**data)  # type: ignore
        else:
            raise ValueError(f"Unsupported region: {self.region} and type: {self.type}")

    async def _start_streaming(self) -> None:
        """Start the SSE streaming connection."""
        url = self._build_stream_url()
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self.base_client.api_key}",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        error_msg = f"Stream failed: {response.status_code} - {error_body.decode()}"
                        await self._put_error(error_msg)
                        return

                    await self._process_stream_lines(response)

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            await self._put_error(f"Connection error: {e}")
        except Exception as e:
            await self._put_error(f"Streaming error: {e}")
        finally:
            self._is_closed = True

    async def _process_stream_lines(self, response) -> None:
        """Process individual lines from the SSE stream."""
        async for line in response.aiter_lines():
            if self._is_closed:
                break

            if not line.startswith("data:"):
                continue

            try:
                # Parse the JSON data after "data:" prefix
                json_data = line[5:]  # Remove "data:" prefix
                parsed_data = json.loads(json_data)

                # Create appropriate model and put in queue
                model_data = self._create_model_from_data(parsed_data)
                result = LivePriceResult[T](data=model_data)
                await self._queue.put(result)

            except (json.JSONDecodeError, Exception) as e:
                await self._put_error(f"Error processing data: {e}")
                break  # Stop processing on errors

    async def _put_error(self, error_message: str) -> None:
        """Put an error result in the queue."""
        if self._queue:
            error_result = LivePriceResult[T](error=error_message)
            await self._queue.put(error_result)


class BidAskStream:
    """Handles bid/ask price streaming for Turkish (BIST) stocks."""

    def __init__(self, base_client):
        self.base_client = base_client
        self._task: Optional[asyncio.Task] = None
        self._queue: Optional[asyncio.Queue] = None
        self._is_closed = False
        self._symbols: List[str] = []

    async def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to bid/ask price updates for given BIST symbols."""
        await self._cleanup_existing_stream()

        self._symbols = symbols
        self._queue = asyncio.Queue()
        self._is_closed = False
        self._task = asyncio.create_task(self._start_streaming())

    async def receive(self) -> AsyncGenerator[BidAskResult, None]:
        """Receive bid/ask price data from the stream."""
        if not self._queue:
            raise RuntimeError("Not subscribed. Call subscribe() first.")

        while not self._is_closed:
            try:
                result = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield result
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def close(self) -> None:
        """Close the stream and cleanup resources."""
        if self._is_closed:
            return

        self._is_closed = True
        await self._cleanup_existing_stream()

    async def _cleanup_existing_stream(self) -> None:
        """Cancel and cleanup existing streaming task."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def _build_stream_url(self) -> str:
        """Build the streaming URL for bid/ask prices."""
        stream_id = str(uuid.uuid4())
        symbols_param = ",".join(self._symbols) if self._symbols else ""
        return f"{self.base_client.base_url}/v1/stock/price/bids?filter={symbols_param}&region=tr&stream={stream_id}"

    def _create_model_from_data(self, data: dict) -> BidAskData:
        """Create bid/ask data model from the received data."""
        # Handle nested data structure from the response
        if "d" in data and isinstance(data["d"], dict):
            bid_ask_data = data["d"]
            return BISTBidAskData(**bid_ask_data)
        else:
            # Fallback for direct data structure
            return BISTBidAskData(**data)

    async def _start_streaming(self) -> None:
        """Start the SSE streaming connection for bid/ask prices."""
        url = self._build_stream_url()
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self.base_client.api_key}",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        error_msg = f"Bid/Ask stream failed: {response.status_code} - {error_body.decode()}"
                        await self._put_error(error_msg)
                        return

                    await self._process_stream_lines(response)

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            await self._put_error(f"Connection error: {e}")
        except Exception as e:
            await self._put_error(f"Bid/Ask streaming error: {e}")
        finally:
            self._is_closed = True

    async def _process_stream_lines(self, response) -> None:
        """Process individual lines from the SSE stream."""
        async for line in response.aiter_lines():
            if self._is_closed:
                break

            if not line.startswith("data:"):
                continue

            try:
                # Parse the JSON data after "data:" prefix
                json_data = line[5:]  # Remove "data:" prefix
                parsed_data = json.loads(json_data)

                # Create bid/ask model and put in queue
                model_data = self._create_model_from_data(parsed_data)
                result = BidAskResult(data=model_data)
                await self._queue.put(result)

            except (json.JSONDecodeError, Exception) as e:
                await self._put_error(f"Error processing bid/ask data: {e}")
                break  # Stop processing on errors

    async def _put_error(self, error_message: str) -> None:
        """Put an error result in the queue."""
        if self._queue:
            error_result = BidAskResult(error=error_message)
            await self._queue.put(error_result)


class LivePriceClient:
    """Main client for live price functionality."""

    def __init__(self, base_client):
        self.base_client = base_client

    async def get_live_price_for_bist(
        self, symbols: List[str]
    ) -> LivePriceStream[LiveMessageV2[BISTStockLiveData]]:
        """Start streaming BIST stock prices.

        Args:
            symbols: List of BIST stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for BIST stocks
        """
        stream: LivePriceStream[LiveMessageV2[BISTStockLiveData]] = LivePriceStream(
            self.base_client, LivePriceType.PRICE, Region.TR
        )
        await stream.subscribe(symbols)
        return stream

    async def get_live_price_for_us(self, symbols: List[str]) -> LivePriceStream[USStockLiveData]:
        """Start streaming US stock prices.

        Args:
            symbols: List of US stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for US stocks
        """
        stream: LivePriceStream[USStockLiveData] = LivePriceStream(
            self.base_client, LivePriceType.PRICE, Region.US
        )
        await stream.subscribe(symbols)
        return stream

    async def get_live_order_book_for_bist(
        self, symbols: List[str]
    ) -> LivePriceStream[BISTStockOrderBookData]:
        """Start streaming BIST order book.

        Args:
            symbols: List of BIST stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for BIST order book
        """
        stream: LivePriceStream[BISTStockOrderBookData] = LivePriceStream(
            self.base_client, LivePriceType.ORDER_BOOK, Region.TR
        )
        await stream.subscribe(symbols)
        return stream

    async def get_live_delayed_price_for_bist(
        self, symbols: List[str]
    ) -> LivePriceStream[LiveMessageV2[BISTStockLiveData]]:
        """Start streaming BIST delayed price.

        Args:
            symbols: List of BIST stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for BIST delayed price
        """
        stream: LivePriceStream[LiveMessageV2[BISTStockLiveData]] = LivePriceStream(
            self.base_client, LivePriceType.DELAYED_PRICE, Region.TR
        )
        await stream.subscribe(symbols)
        return stream

    async def get_bid_ask_for_bist(self, symbols: List[str]) -> BidAskStream:
        """Start streaming BIST bid/ask prices.

        Args:
            symbols: List of BIST stock symbols (empty for all stocks)

        Returns:
            BidAskStream for BIST stocks bid/ask data
        """
        stream = BidAskStream(self.base_client)
        await stream.subscribe(symbols)
        return stream
