import asyncio
import json
import urllib.parse
from typing import AsyncGenerator, Dict, Generic, List, Optional

import httpx

from laplace.base import BaseClient

from .models import (
    Locale,
    News,
    NewsV2,
    NewsApiSourceListItem,
    NewsCategoryListItem,
    NewsHighlight,
    NewsLane,
    NewsLaneListItem,
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

    def __init__(
        self,
        base_client: BaseClient,
        locale: Locale,
        region: Region,
        lane: Optional[NewsLane] = None,
        sectors: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        api_sources: Optional[List[str]] = None,
    ):
        self.base_client = base_client
        self.locale = locale
        self.region = region
        self.lane = lane
        self.sectors = sectors
        self.tickers = tickers
        self.categories = categories
        self.industries = industries
        self.api_sources = api_sources
        self._task: Optional[asyncio.Task] = None
        self._queue: Optional[asyncio.Queue[NewsStreamResult[List[NewsV2]]]] = None
        self._is_closed = False

    async def subscribe(self) -> None:
        """Subscribe to news updates stream."""
        await self._cleanup_existing_stream()

        self._queue = asyncio.Queue[NewsStreamResult[List[NewsV2]]]()
        self._is_closed = False
        self._task = asyncio.create_task(self._start_streaming())

    async def receive(self) -> AsyncGenerator[NewsStreamResult[List[NewsV2]], None]:
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

    def __aiter__(self) -> AsyncGenerator[NewsStreamResult[List[NewsV2]], None]:
        """Allow ``async for result in stream`` directly over the stream."""
        return self.receive()

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
        url = f"{self.base_client.base_url}/v1/news/stream"
        params = {"locale": self.locale, "region": self.region.value}
        if self.lane is not None:
            params["lane"] = self.lane.value
        if self.sectors:
            params["sectors"] = ",".join(self.sectors)
        if self.tickers:
            params["tickers"] = ",".join(self.tickers)
        if self.categories:
            params["categories"] = ",".join(self.categories)
        if self.industries:
            params["industries"] = ",".join(self.industries)
        if self.api_sources:
            params["apiSource"] = ",".join(self.api_sources)

        query_string = urllib.parse.urlencode(params)
        return f"{url}?{query_string}"

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
                news_items = [NewsV2(**item) for item in parsed_data]
                result = NewsStreamResult[List[NewsV2]](data=news_items)
                await self._queue.put(result)

            except Exception as e:
                await self._put_error(f"Error processing news data: {e}")
                continue

    async def _put_error(self, error_message: str) -> None:
        """Put an error result in the queue."""
        if self._queue:
            error_result = NewsStreamResult[List[NewsV2]](error=error_message)
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
        lane: Optional[NewsLane] = None,
        api_source: Optional[str] = None,
        symbols: Optional[str] = None,
        categories: Optional[str] = None,
        sectors: Optional[str] = None,
        industries: Optional[str] = None,
        quality_score_min: Optional[int] = None,
        quality_score_max: Optional[int] = None,
        timestamp_from: Optional[str] = None,
        timestamp_to: Optional[str] = None,
        extra_filters: Optional[str] = None,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[News]:
        """Retrieve paginated news.

        Within a single filter, comma-separated values are OR-ed; different
        filters are AND-ed together (e.g. ``(AAPL OR MSFT) AND Technology``).
        The ``categories``, ``sectors`` and ``industries`` filters only accept
        values returned by their respective listing endpoints
        (``/api/v1/news/categories`` ``name``, ``/api/v1/sector`` ``title``,
        ``/api/v1/industry`` ``title``).

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (e.g. Region.TR)
            news_type: Optional news type filter
            news_order_by: Optional sorting field (timestamp, quality_score)
            direction: Optional sort direction
            lane: Optional lane filter. Lanes are region-scoped: US lanes are
                GLOBAL_MACRO and FAST_MOVERS; TR lanes are TR_EKONOMI and BIST.
            api_source: Optional comma-separated source ids from
                :meth:`get_news_api_source_names` (e.g. "BBCBusiness,MarketWatch")
            symbols: Optional comma-separated ticker symbols (e.g. "AAPL,MSFT")
            categories: Optional comma-separated category names
            sectors: Optional comma-separated sector titles
            industries: Optional comma-separated industry titles
            quality_score_min: Optional minimum quality score, inclusive (0-10)
            quality_score_max: Optional maximum quality score, inclusive (0-10)
            timestamp_from: Optional start date, inclusive (YYYY-MM-DD)
            timestamp_to: Optional end date, inclusive (YYYY-MM-DD)
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
        if lane is not None:
            params["lane"] = lane.value
        if api_source:
            params["apiSource"] = api_source
        if symbols:
            params["symbols"] = symbols
        if categories:
            params["categories"] = categories
        if sectors:
            params["sectors"] = sectors
        if industries:
            params["industries"] = industries
        if quality_score_min is not None:
            params["qualityScoreMin"] = quality_score_min
        if quality_score_max is not None:
            params["qualityScoreMax"] = quality_score_max
        if timestamp_from:
            params["timestampFrom"] = timestamp_from
        if timestamp_to:
            params["timestampTo"] = timestamp_to
        if extra_filters:
            params["extraFilters"] = extra_filters

        response = self._client.get("v1/news", params=params)
        return PaginatedResponse[News](**response)

    def get_news_v2(
        self,
        locale: Locale,
        region: Region,
        news_type: Optional[NewsType] = None,
        news_order_by: Optional[NewsOrderBy] = None,
        direction: Optional[SortDirection] = None,
        lane: Optional[NewsLane] = None,
        api_source: Optional[str] = None,
        symbols: Optional[str] = None,
        categories: Optional[str] = None,
        sectors: Optional[str] = None,
        industries: Optional[str] = None,
        quality_score_min: Optional[int] = None,
        quality_score_max: Optional[int] = None,
        timestamp_from: Optional[str] = None,
        timestamp_to: Optional[str] = None,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[NewsV2]:
        """Retrieve paginated news (v2).

        Within a single filter, comma-separated values are OR-ed; different
        filters are AND-ed together (e.g. ``(AAPL OR MSFT) AND Technology``).
        The ``categories``, ``sectors`` and ``industries`` filters only accept
        values returned by their respective listing endpoints
        (``/api/v1/news/categories`` ``name``, ``/api/v1/sector`` ``title``,
        ``/api/v1/industry`` ``title``).

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (e.g. Region.TR)
            news_type: Optional news type filter
            news_order_by: Optional sorting field (timestamp, quality_score)
            direction: Optional sort direction
            lane: Optional lane filter. Lanes are region-scoped: US lanes are
                GLOBAL_MACRO and FAST_MOVERS; TR lanes are TR_EKONOMI and BIST.
            api_source: Optional comma-separated source ids from
                :meth:`get_news_api_source_names` (e.g. "BBCBusiness,MarketWatch")
            symbols: Optional comma-separated ticker symbols (e.g. "AAPL,MSFT")
            categories: Optional comma-separated category names
            sectors: Optional comma-separated sector titles
            industries: Optional comma-separated industry titles
            quality_score_min: Optional minimum quality score, inclusive (0-10)
            quality_score_max: Optional maximum quality score, inclusive (0-10)
            timestamp_from: Optional start date, inclusive (YYYY-MM-DD)
            timestamp_to: Optional end date, inclusive (YYYY-MM-DD)
            page: Page number (default: 0)
            page_size: Page size enum (default: 10)

        Returns:
            PaginatedResponse[NewsV2]
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
        if lane is not None:
            params["lane"] = lane.value
        if api_source:
            params["apiSource"] = api_source
        if symbols:
            params["symbols"] = symbols
        if categories:
            params["categories"] = categories
        if sectors:
            params["sectors"] = sectors
        if industries:
            params["industries"] = industries
        if quality_score_min is not None:
            params["qualityScoreMin"] = quality_score_min
        if quality_score_max is not None:
            params["qualityScoreMax"] = quality_score_max
        if timestamp_from:
            params["timestampFrom"] = timestamp_from
        if timestamp_to:
            params["timestampTo"] = timestamp_to

        response = self._client.get("v2/news", params=params)
        return PaginatedResponse[NewsV2](**response)

    def get_news_categories(
        self,
        locale: Optional[Locale] = None,
    ) -> List[NewsCategoryListItem]:
        """Retrieve the full canonical news category list.

        Always returns every category regardless of whether it currently has
        tagged news, ordered by id ascending. The returned ``name`` values are
        the exact values accepted by the ``categories`` filter of
        :meth:`get_news_v2` and :meth:`get_news_stream`.

        Args:
            locale: Optional language code ("tr", "en"). Defaults to "en";
                any unsupported value falls back to "en".

        Returns:
            List of NewsCategoryListItem
        """
        params: Dict[str, object] = {}
        if locale is not None:
            params["locale"] = locale

        response = self._client.get("v1/news/categories", params=params)
        return [NewsCategoryListItem(**item) for item in response]

    def get_news_lanes(self) -> List[NewsLaneListItem]:
        """Retrieve the fixed news lane list.

        Returns every lane (``id`` + ``label``) for building a lane filter. The
        returned ``id`` values are the exact values accepted by the ``lane``
        filter of :meth:`get_news`, :meth:`get_news_v2` and
        :meth:`get_news_stream` (see :class:`~laplace.models.NewsLane`).

        Returns:
            List of NewsLaneListItem
        """
        response = self._client.get("v1/news/lanes")
        return [NewsLaneListItem(**item) for item in response]

    def get_news_api_source_names(self) -> List[NewsApiSourceListItem]:
        """Retrieve the configured news sources.

        Returns every source (``id`` + ``name``), registry sources first, then
        any legacy sources still on old rows. The returned ``id`` values are
        the exact values accepted by the ``api_source`` filter of
        :meth:`get_news` and :meth:`get_news_v2` and the ``api_sources``
        filter of :meth:`get_news_stream`; ``name`` is the display name
        (e.g. "BBC Business").

        Returns:
            List of NewsApiSourceListItem
        """
        response = self._client.get("v1/news/api-source-names")
        return [NewsApiSourceListItem(**item) for item in response]

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

    async def get_news_stream(
        self,
        locale: Locale,
        region: Region,
        lane: Optional[NewsLane] = None,
        sectors: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        api_sources: Optional[List[str]] = None,
    ) -> NewsStream:
        """Start streaming news updates.

        Args:
            locale: Locale code (e.g., "tr", "en")
            region: Region enum (e.g. Region.TR)
            lane: Optional lane filter. Lanes are region-scoped: US lanes are
                GLOBAL_MACRO and FAST_MOVERS; TR lanes are TR_EKONOMI and BIST.
            sectors: Optional list of sectors
            tickers: Optional list of tickers (stream uses tickers, not symbols)
            categories: Optional list of categories
            industries: Optional list of industries
            api_sources: Optional list of source ids from
                :meth:`get_news_api_source_names`; only these sources are
                streamed

        Returns:
            NewsStream for consuming news items
        """
        stream = NewsStream(
            self._client,
            locale,
            region,
            lane=lane,
            sectors=sectors,
            tickers=tickers,
            categories=categories,
            industries=industries,
            api_sources=api_sources,
        )
        await stream.subscribe()
        return stream
