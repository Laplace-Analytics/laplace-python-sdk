"""Live price streaming functionality for Laplace API."""

import asyncio
import json
import uuid
from typing import AsyncGenerator, Optional, Union, List
import httpx
from laplace.models import Region, BISTStockLiveData, USStockLiveData

LivePriceData = Union[BISTStockLiveData, USStockLiveData]


class LivePriceResult:
    """Result wrapper for live price data."""

    def __init__(self, data: Optional[LivePriceData] = None, error: Optional[str] = None):
        self.data = data
        self.error = error

    @property
    def is_error(self) -> bool:
        return self.error is not None


class LivePriceStream:
    """Handles live price streaming for a specific region."""

    def __init__(self, base_client, region: Region):
        self.base_client = base_client
        self.region = region
        self._task: Optional[asyncio.Task] = None
        self._queue: Optional[asyncio.Queue] = None
        self._is_closed = False
        self._symbols: List[str] = []

    async def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to live price updates for given symbols."""
        await self._cleanup_existing_stream()

        self._symbols = symbols
        self._queue = asyncio.Queue()
        self._is_closed = False
        self._task = asyncio.create_task(self._start_streaming())

    async def receive(self) -> AsyncGenerator[LivePriceResult, None]:
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
        return f"{self.base_client.base_url}/v1/stock/price/live?filter={symbols_param}&region={self.region}&stream={stream_id}"

    def _create_model_from_data(self, data: dict) -> LivePriceData:
        """Create appropriate data model based on region."""
        if self.region == "tr":
            return BISTStockLiveData(**data)
        elif self.region == "us":
            return USStockLiveData(**data)
        else:
            raise ValueError(f"Unsupported region: {self.region}")

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
                result = LivePriceResult(data=model_data)
                await self._queue.put(result)

            except (json.JSONDecodeError, Exception) as e:
                await self._put_error(f"Error processing data: {e}")
                break  # Stop processing on errors

    async def _put_error(self, error_message: str) -> None:
        """Put an error result in the queue."""
        if self._queue:
            error_result = LivePriceResult(error=error_message)
            await self._queue.put(error_result)


class LivePriceClient:
    """Main client for live price functionality."""

    def __init__(self, base_client):
        self.base_client = base_client

    async def get_live_price_for_bist(self, symbols: List[str]) -> LivePriceStream:
        """Start streaming BIST stock prices.

        Args:
            symbols: List of BIST stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for BIST stocks
        """
        stream = LivePriceStream(self.base_client, "tr")
        await stream.subscribe(symbols)
        return stream

    async def get_live_price_for_us(self, symbols: List[str]) -> LivePriceStream:
        """Start streaming US stock prices.

        Args:
            symbols: List of US stock symbols (empty for all stocks)

        Returns:
            LivePriceStream for US stocks
        """
        stream = LivePriceStream(self.base_client, "us")
        await stream.subscribe(symbols)
        return stream