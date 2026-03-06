import asyncio
import json
from typing import AsyncGenerator, Dict, Generic, List, Optional

import httpx

from laplace.base import BaseClient

from .models import (
    Locale,
    News,
    NewsHighlight,
    NewsOrderBy,
    NewsType,
    PaginatedResponse,
    PaginationPageSize,
    Region,
    SortDirection,
    T,
)


class NewsStreamResult(Generic[T]):
    """Result wrapper for news stream data."""

    def __init__(self, data: Optional[T] = None, error: Optional[str] = None):
        self.data = data
        self.error = error

    @property
    def is_error(self) -> bool:
        return self.error is not None


class NewsStream:
    """Handles Server-Sent Events (SSE) stream for news."""

    def __init__(self, base_client: BaseClient, locale: Locale):
        self.base_client = base_client
        self.locale = locale
        self._task: Optional[asyncio.Task] = None
        self._queue: Optional[asyncio.Queue[NewsStreamResult[List[News]]]] = None
        self._is_closed = False

    async def subscribe(self) -> None:
        """Subscribe to news updates stream."""
        await self._cleanup_existing_stream()

        self._queue = asyncio.Queue[NewsStreamResult[List[News]]]()
        self._is_closed = False
        self._task = asyncio.create_task(self._start_streaming())

    async def receive(self) -> AsyncGenerator[NewsStreamResult[List[News]], None]:
        """Receive news data from the stream."""
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
        """Build the streaming URL for the news endpoint."""
        url = self.base_client.base_url
        return f"{url}/v1/news/stream?locale={self.locale}"

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
                        error_msg = f"News stream failed: {response.status_code} - "
                        error_msg += f"{error_body.decode()}"
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
                json_data = line[5:].strip()  # Remove "data:" prefix
                if not json_data:
                    continue

                parsed_data = json.loads(json_data)

                # Process array of news items
                news_items = [News(**item) for item in parsed_data]
                result = NewsStreamResult[List[News]](data=news_items)
                await self._queue.put(result)

            except Exception as e:
                await self._put_error(f"Error processing news data: {e}")
                continue

    async def _put_error(self, error_message: str) -> None:
        """Put an error result in the queue."""
        if self._queue:
            error_result = NewsStreamResult[List[News]](error=error_message)
            await self._queue.put(error_result)


class NewsClient:
    """Client for news API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the news client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_news(
        self,
        locale: Locale,
        region: Region,
        news_type: Optional[NewsType] = None,
        news_order_by: Optional[NewsOrderBy] = None,
        direction: Optional[SortDirection] = None,
        extra_filters: Optional[str] = None,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[News]:
        """Retrieve paginated news.

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (e.g. Region.TR)
            news_type: Optional news type filter
            news_order_by: Optional sorting field
            direction: Optional sort direction
            extra_filters: Optional extra filters (API-specific)
            page: Page number (default: 0)
            page_size: Page size enum (default: 10)

        Returns:
            PaginatedResponse[News]
        """
        params: Dict[str, object] = {
            "locale": locale,
            "region": region.value,
            "page": page,
            "size": page_size.value,
        }

        if news_type is not None:
            params["newsType"] = news_type.value
        if news_order_by is not None:
            params["orderBy"] = news_order_by.value
        if direction is not None:
            params["orderByDirection"] = direction.value
        if extra_filters:
            params["extraFilters"] = extra_filters

        response = self._client.get("v1/news", params=params)
        return PaginatedResponse[News](**response)

    def get_highlights(
        self,
        locale: Locale,
        region: Region
    ) -> NewsHighlight:
        """Retrieve news highlights.

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (e.g. Region.TR)

        Returns:
            NewsHighlight
        """
        params: Dict[str, object] = {
            "locale": locale,
            "region": region.value
        }

        response = self._client.get("v1/news/highlights", params=params)
        return NewsHighlight(**response)

    async def get_news_stream(self, locale: Locale) -> NewsStream:
        """Start streaming news updates.

        Args:
            locale: Locale code (e.g., "tr", "en")

        Returns:
            NewsStream for consuming news items
        """
        stream = NewsStream(self._client, locale)
        await stream.subscribe()
        return stream
