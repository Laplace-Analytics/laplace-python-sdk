"""Live price streaming functionality for Laplace API."""

import json
import uuid
from typing import AsyncGenerator

import httpx
from pydantic import BaseModel, Field

from laplace.models import Region

from .base import LaplaceAPIError


class BISTStockLiveData(BaseModel):
    """BIST (Turkish) stock live data model."""

    symbol: str = Field(alias="s")
    daily_percent_change: float = Field(alias="ch")
    close_price: float = Field(alias="p")
    date: int = Field(alias="d")


class USStockLiveData(BaseModel):
    """US stock live data model."""

    symbol: str = Field(alias="s")
    price: float = Field(alias="p")
    date: int = Field(alias="d")


class LivePriceClient:
    """Client for live price streaming functionality."""

    def __init__(self, base_client):
        """Initialize the live price client.

        Args:
            base_client: The base Laplace client
        """
        self.base_client = base_client

    def _get_live_price_url(self, symbols: list[str], region: Region) -> str:
        """Construct the live price streaming URL.

        Args:
            symbols: List of stock symbols
            region: Region code (TR, US, etc.)

        Returns:
            Constructed URL for live price streaming
        """
        stream_id = str(uuid.uuid4())
        symbols_str = ",".join(symbols)
        return f"{self.base_client.base_url}/v1/stock/price/live?filter={symbols_str}&region={region}&stream={stream_id}"

    async def _stream_sse_events(self, url: str, headers: dict) -> AsyncGenerator[dict, None]:
        """Stream Server-Sent Events from the API.

        Args:
            url: The SSE endpoint URL
            headers: Request headers including authorization

        Yields:
            Parsed event data as dictionaries
        """
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=headers) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    raise LaplaceAPIError(
                        message=f"Live price stream failed: {response.status_code}",
                        status_code=response.status_code,
                        response={"error": error_body.decode()},
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = line[5:]  # Remove "data:" prefix
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError as e:
                            # Log error but continue streaming
                            print(f"Error parsing SSE data: {e}")
                            continue

    async def get_live_price_for_bist(
        self, symbols: list[str]
    ) -> AsyncGenerator[BISTStockLiveData, None]:
        """Stream real-time price data for BIST (Turkish) stock symbols.

        Args:
            symbols: List of BIST stock symbols

        Yields:
            BISTStockLiveData objects with live price information
        """
        print(f"Getting live price for BIST symbols: {symbols}")
        print(f"API Key: {self.base_client.api_key}")
        print(f"Base URL: {self.base_client.base_url}")
        print(f"URL: {self._get_live_price_url(symbols, 'TR')}")

        url = self._get_live_price_url(symbols, "tr")
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self.base_client.api_key}",
        }

        async for event_data in self._stream_sse_events(url, headers):
            try:
                yield BISTStockLiveData(**event_data)
            except Exception as e:
                print(f"Error parsing BIST live data: {e}")
                continue

    async def get_live_price_for_us(
        self, symbols: list[str]
    ) -> AsyncGenerator[USStockLiveData, None]:
        """Stream real-time price data for US stock symbols.

        Args:
            symbols: List of US stock symbols

        Yields:
            USStockLiveData objects with live price information
        """
        url = self._get_live_price_url(symbols, "us")
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self.base_client.api_key}",
        }

        async for event_data in self._stream_sse_events(url, headers):
            try:
                yield USStockLiveData(**event_data)
            except Exception as e:
                print(f"Error parsing US live data: {e}")
                continue
