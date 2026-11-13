import asyncio
import json
import urllib.parse
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import httpx

from laplace.base import BaseClient

from .models import (
    Locale,
    News,
    NewsV2,
    NewsApiSourceListItem,
    NewsCategoryListItem,
    NewsEventType,
    NewsEventTypeInfo,
    NewsHighlight,
    NewsLane,
    NewsLaneListItem,
    NewsOrderBy,
    NewsTickerRelevance,
    NewsType,
    NewsV2Page,
    PaginatedResponse,
    PaginationPageSize,
    Region,
    SortDirection,
    T,
)


# Filters that take one or more values accept a list (joined with commas) or a
# ready-made comma-separated string. Enum members and plain strings can be mixed,
# so values the SDK doesn't list yet can still be sent.
StrList = Union[str, Sequence[Union[str, Enum]]]
TickerRelevanceFilter = Union[str, Sequence[Union[NewsTickerRelevance, str]]]
EventTypeFilter = Union[str, Sequence[Union[NewsEventType, str]]]
OrderByField = Union[NewsOrderBy, str]
# A sort field, or a (field, direction) pair; a direction of None uses the API default (desc).
NewsOrder = Union[OrderByField, Tuple[OrderByField, Optional[Union[SortDirection, str]]]]
TimeValue = Union[str, datetime]


def _value(v: Union[str, Enum]) -> str:
    return v.value if isinstance(v, Enum) else str(v)


def _join(values: StrList) -> str:
    if isinstance(values, str):
        return values
    return ",".join(_value(v) for v in values)


def _bool(v: bool) -> str:
    return "true" if v else "false"


def _time(v: TimeValue) -> str:
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return v


def _order(fields: Sequence[NewsOrder]) -> str:
    parts = []
    for f in fields:
        if isinstance(f, tuple):
            field, direction = f
            parts.append(_value(field) + (f" {_value(direction)}" if direction else ""))
        else:
            parts.append(_value(f))
    return ",".join(parts)


def _content_filter_params(
    ticker_relevance: Optional[TickerRelevanceFilter],
    exclude_list_articles: Optional[bool],
    event_types: Optional[EventTypeFilter],
    exclude_event_types: Optional[EventTypeFilter],
    collapse_clusters: Optional[bool],
) -> Dict[str, str]:
    """Query params for the content filters shared by /v2/news and the stream."""
    params: Dict[str, str] = {}
    if ticker_relevance:
        params["tickerRelevance"] = _join(ticker_relevance)
    if exclude_list_articles is not None:
        params["excludeListArticles"] = _bool(exclude_list_articles)
    if event_types:
        params["eventTypes"] = _join(event_types)
    if exclude_event_types:
        params["excludeEventTypes"] = _join(exclude_event_types)
    if collapse_clusters is not None:
        params["collapseClusters"] = _bool(collapse_clusters)
    return params


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
        symbols: Optional[List[str]] = None,
        category_ids: Optional[List[str]] = None,
        sector_ids: Optional[List[str]] = None,
        industry_ids: Optional[List[str]] = None,
        api_sources: Optional[List[str]] = None,
        ticker_relevance: Optional[TickerRelevanceFilter] = None,
        exclude_list_articles: Optional[bool] = None,
        event_types: Optional[EventTypeFilter] = None,
        exclude_event_types: Optional[EventTypeFilter] = None,
        collapse_clusters: Optional[bool] = None,
    ):
        self.base_client = base_client
        self.locale = locale
        self.region = region
        self.lane = lane
        self.symbols = symbols
        self.category_ids = category_ids
        self.sector_ids = sector_ids
        self.industry_ids = industry_ids
        self.api_sources = api_sources
        self.ticker_relevance = ticker_relevance
        self.exclude_list_articles = exclude_list_articles
        self.event_types = event_types
        self.exclude_event_types = exclude_event_types
        self.collapse_clusters = collapse_clusters
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
        if self.symbols:
            params["symbols"] = ",".join(self.symbols)
        if self.category_ids:
            params["categoryIds"] = ",".join(self.category_ids)
        if self.sector_ids:
            params["sectorIds"] = ",".join(self.sector_ids)
        if self.industry_ids:
            params["industryIds"] = ",".join(self.industry_ids)
        if self.api_sources:
            params["apiSource"] = ",".join(self.api_sources)
        params.update(
            _content_filter_params(
                self.ticker_relevance,
                self.exclude_list_articles,
                self.event_types,
                self.exclude_event_types,
                self.collapse_clusters,
            )
        )

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
        category_ids: Optional[str] = None,
        sector_ids: Optional[str] = None,
        industry_ids: Optional[str] = None,
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
        filters are AND-ed together (e.g. ``(AAPL OR MSFT) AND category 1``).
        The taxonomy filters are ID-based: ``category_ids`` takes the numeric
        ids returned by :meth:`get_news_categories`; ``sector_ids`` and
        ``industry_ids`` take Laplace sector/industry ids.

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
            category_ids: Optional comma-separated numeric category ids (e.g. "1,3")
            sector_ids: Optional comma-separated Laplace sector ids
            industry_ids: Optional comma-separated Laplace industry ids
            quality_score_min: Optional minimum quality score, inclusive (0-10)
            quality_score_max: Optional maximum quality score, inclusive (0-10)
            timestamp_from: Optional start date, inclusive (YYYY-MM-DD).
                Deprecated by the API; on v2 use ``published_from``.
            timestamp_to: Optional end date, inclusive (YYYY-MM-DD).
                Deprecated by the API; on v2 use ``published_to``.
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
        if category_ids:
            params["categoryIds"] = category_ids
        if sector_ids:
            params["sectorIds"] = sector_ids
        if industry_ids:
            params["industryIds"] = industry_ids
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
        news_order_by: Optional[OrderByField] = None,
        direction: Optional[SortDirection] = None,
        lane: Optional[NewsLane] = None,
        api_source: Optional[str] = None,
        symbols: Optional[StrList] = None,
        category_ids: Optional[StrList] = None,
        sector_ids: Optional[StrList] = None,
        industry_ids: Optional[StrList] = None,
        quality_score_min: Optional[int] = None,
        quality_score_max: Optional[int] = None,
        timestamp_from: Optional[str] = None,
        timestamp_to: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Union[PaginationPageSize, int] = PaginationPageSize.PAGE_SIZE_10,
        *,
        ticker_relevance: Optional[TickerRelevanceFilter] = None,
        exclude_list_articles: Optional[bool] = None,
        event_types: Optional[EventTypeFilter] = None,
        exclude_event_types: Optional[EventTypeFilter] = None,
        collapse_clusters: Optional[bool] = None,
        max_publisher_share: Optional[int] = None,
        published_from: Optional[TimeValue] = None,
        published_to: Optional[TimeValue] = None,
        updated_since: Optional[TimeValue] = None,
        as_of: Optional[TimeValue] = None,
        order_by: Optional[Sequence[NewsOrder]] = None,
        cursor: Optional[str] = None,
        include_total: Optional[bool] = None,
    ) -> NewsV2Page:
        """Retrieve a page of news (v2), newest first by default.

        Within a single filter, comma-separated values are OR-ed; different
        filters are AND-ed together (e.g. ``(AAPL OR MSFT) AND category 1``).
        The taxonomy filters are ID-based: ``category_ids`` takes the numeric
        ids returned by :meth:`get_news_categories`; ``sector_ids`` and
        ``industry_ids`` take Laplace sector/industry ids.

        Multi-value filters take a list or a comma-separated string. Enum
        values and plain strings are both accepted; the API rejects unknown
        values with a 400 (:class:`~laplace.base.LaplaceAPIError`, message in
        ``error.response["message"]``). Unset filters aren't sent.

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (e.g. Region.TR)
            news_type: Optional news type filter
            news_order_by: Optional single sorting field (see
                :class:`~laplace.models.NewsOrderBy`)
            direction: Optional sort direction for ``news_order_by``
            lane: Optional lane filter. Lanes are region-scoped: US lanes are
                GLOBAL_MACRO and FAST_MOVERS; TR lanes are TR_EKONOMI and BIST.
            api_source: Optional comma-separated source ids from
                :meth:`get_news_api_source_names` (e.g. "BBCBusiness,MarketWatch")
            symbols: Optional ticker symbols, up to 50 (e.g. ["AAPL", "MSFT"])
            category_ids: Optional numeric category ids (e.g. "1,3")
            sector_ids: Optional Laplace sector ids
            industry_ids: Optional Laplace industry ids
            quality_score_min: Optional minimum quality score, inclusive
                (0-10). The API default is 3; send 0 to include unscored items.
            quality_score_max: Optional maximum quality score, inclusive (0-10)
            timestamp_from: Deprecated; use ``published_from``.
            timestamp_to: Deprecated; use ``published_to``.
            page: Optional page number for offset paging. Can't be combined
                with ``cursor``. Sent as 0 when neither is given, as before.
            page_size: Items per page, 1-100 (int or PaginationPageSize;
                default: 10)
            ticker_relevance: Keep news where a ticker (one of ``symbols``, if
                given) has one of these relevances
            exclude_list_articles: ``True`` drops market wraps, "most traded"
                lists and top-gainer tables
            event_types: Keep only these event types
            exclude_event_types: Drop these event types (unclassified kept)
            collapse_clusters: ``True`` returns each story once
            max_publisher_share: 1-100 (percent); limits how much of the
                result one publisher can take. See ``publisher_cap``.
            published_from: Lower bound on ``published_at`` (RFC3339 string,
                YYYY-MM-DD, or datetime; naive datetimes are read as UTC)
            published_to: Upper bound on ``published_at``; a date includes
                the whole day
            updated_since: Lower bound on ``updated_at``, for incremental
                sync. Changes the default order to updatedAt ascending.
            as_of: Return the result as it was at that time
            order_by: Up to 3 sort fields, each a field or a
                ``(field, direction)`` pair, e.g.
                ``[(NewsOrderBy.QUALITY_SCORE_V2, SortDirection.DESC),
                (NewsOrderBy.PUBLISHED_AT, SortDirection.DESC)]``.
                Replaces ``news_order_by`` / ``direction``. Cursors only work
                with a single field.
            cursor: ``next_cursor`` from the previous page. An empty string
                requests the first page of a cursor run (no ``page`` sent).
            include_total: ``False`` skips counting all matches (faster);
                ``record_count`` is then ``None``

        Returns:
            NewsV2Page (a PaginatedResponse[NewsV2] with ``next_cursor`` and
            ``publisher_cap``)
        """
        params: Dict[str, object] = {
            "locale": locale,
            "region": region.value,
            "size": int(page_size),
        }
        if page is not None:
            params["page"] = page
        elif cursor is None:
            # Keep the request unchanged for callers that relied on the old default.
            params["page"] = 0

        if news_type is not None:
            params["newsType"] = news_type.value
        if order_by:
            params["orderBy"] = _order(order_by)
        else:
            if news_order_by is not None:
                params["orderBy"] = _value(news_order_by)
            if direction is not None:
                params["orderByDirection"] = direction.value
        if lane is not None:
            params["lane"] = lane.value
        if api_source:
            params["apiSource"] = api_source
        if symbols:
            params["symbols"] = _join(symbols)
        if category_ids:
            params["categoryIds"] = _join(category_ids)
        if sector_ids:
            params["sectorIds"] = _join(sector_ids)
        if industry_ids:
            params["industryIds"] = _join(industry_ids)
        if quality_score_min is not None:
            params["qualityScoreMin"] = quality_score_min
        if quality_score_max is not None:
            params["qualityScoreMax"] = quality_score_max
        if timestamp_from:
            params["timestampFrom"] = timestamp_from
        if timestamp_to:
            params["timestampTo"] = timestamp_to

        params.update(
            _content_filter_params(
                ticker_relevance,
                exclude_list_articles,
                event_types,
                exclude_event_types,
                collapse_clusters,
            )
        )
        if max_publisher_share is not None:
            params["maxPublisherShare"] = max_publisher_share
        if published_from is not None:
            params["publishedFrom"] = _time(published_from)
        if published_to is not None:
            params["publishedTo"] = _time(published_to)
        if updated_since is not None:
            params["updatedSince"] = _time(updated_since)
        if as_of is not None:
            params["asOf"] = _time(as_of)
        if cursor:
            params["cursor"] = cursor
        if include_total is not None:
            params["includeTotal"] = _bool(include_total)

        response = self._client.get("v2/news", params=params)
        return NewsV2Page(**response)

    def iter_news_v2(self, locale: Locale, region: Region, **kwargs: Any) -> Iterator[NewsV2]:
        """Yield every v2 news item matching the filters, following cursors.

        Takes the same arguments as :meth:`get_news_v2`. Sends
        ``include_total=False`` and keeps every other argument the same
        between pages. Pass ``cursor`` to resume from a saved position.
        ``page`` can't be used, since the API rejects it with a cursor.
        API errors are raised as they happen.

        Example:
            for item in client.news.iter_news_v2("tr", Region.TR, symbols="THYAO",
                                                 page_size=100):
                handle(item)
        """
        if kwargs.get("page") is not None:
            raise ValueError("iter_news_v2 uses cursor paging; don't pass page")
        kwargs.pop("page", None)
        kwargs["include_total"] = False
        kwargs["cursor"] = kwargs.get("cursor") or ""

        while True:
            result = self.get_news_v2(locale, region, **kwargs)
            yield from result.items
            if not result.next_cursor:
                return
            kwargs["cursor"] = result.next_cursor

    def get_news_categories(
        self,
        locale: Optional[Locale] = None,
    ) -> List[NewsCategoryListItem]:
        """Retrieve the full canonical news category list.

        Always returns every category regardless of whether it currently has
        tagged news, ordered by id ascending. The returned numeric ``id``
        values are the exact values accepted by the ``category_ids`` filter of
        :meth:`get_news`, :meth:`get_news_v2` and :meth:`get_news_stream`;
        ``name`` is the display name for dropdowns.

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

    def get_news_event_types(
        self,
        locale: Optional[Locale] = None,
    ) -> List[NewsEventTypeInfo]:
        """Retrieve the event types accepted by ``event_types`` / ``exclude_event_types``.

        Args:
            locale: Optional language of the names ("tr", "en"; default "en")

        Returns:
            List of NewsEventTypeInfo (``slug``, ``name``, ``language``)
        """
        params: Dict[str, object] = {}
        if locale is not None:
            params["locale"] = locale

        response = self._client.get("v1/news/event-types", params=params)
        return [NewsEventTypeInfo(**item) for item in response]

    def get_news_lanes(
        self,
        region: Optional[Region] = None,
    ) -> List[NewsLaneListItem]:
        """Retrieve the fixed news lane list.

        Returns every lane (``id`` + ``label``) for building a lane filter. The
        returned ``id`` values are the exact values accepted by the ``lane``
        filter of :meth:`get_news`, :meth:`get_news_v2` and
        :meth:`get_news_stream` (see :class:`~laplace.models.NewsLane`).

        Args:
            region: Optional region filter; only lanes valid for this region

        Returns:
            List of NewsLaneListItem
        """
        params: Dict[str, object] = {}
        if region is not None:
            params["region"] = region.value

        response = self._client.get("v1/news/lanes", params=params)
        return [NewsLaneListItem(**item) for item in response]

    def get_news_api_source_names(
        self,
        region: Optional[Region] = None,
        language: Optional[Locale] = None,
    ) -> List[NewsApiSourceListItem]:
        """Retrieve the configured news sources.

        Returns every source (``id`` + ``name``), registry sources first, then
        any legacy sources still on old rows. The returned ``id`` values are
        the exact values accepted by the ``api_source`` filter of
        :meth:`get_news` and :meth:`get_news_v2` and the ``api_sources``
        filter of :meth:`get_news_stream`; ``name`` is the display name
        (e.g. "BBC Business").

        Args:
            region: Optional region filter; only sources valid for this region
            language: Optional language filter ("tr", "en"); sources with
                content available in this language

        Returns:
            List of NewsApiSourceListItem
        """
        params: Dict[str, object] = {}
        if region is not None:
            params["region"] = region.value
        if language is not None:
            params["language"] = language

        response = self._client.get("v1/news/api-source-names", params=params)
        return [NewsApiSourceListItem(**item) for item in response]

    def get_highlights(
        self,
        locale: Locale,
        region: Region,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: Optional[int] = None,
        top: Optional[int] = None,
    ) -> PaginatedResponse[NewsHighlight]:
        """Retrieve paginated news highlights, newest first.

        Args:
            locale: Locale code (e.g. "tr", "en")
            region: Region enum (must be Region.US; "tr" is rejected)
            from_date: Optional lower bound, inclusive (YYYY-MM-DD); lists
                highlights created on/after this date
            to_date: Optional upper bound, inclusive of the day (YYYY-MM-DD)
            skip: Optional pagination offset
            top: Optional page size (1-20)

        Returns:
            PaginatedResponse[NewsHighlight]
        """
        params: Dict[str, object] = {
            "locale": locale,
            "region": region.value,
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if skip is not None:
            params["skip"] = skip
        if top is not None:
            params["top"] = top

        response = self._client.get("v1/news/highlights", params=params)
        return PaginatedResponse[NewsHighlight](**response)

    async def get_news_stream(
        self,
        locale: Locale,
        region: Region,
        lane: Optional[NewsLane] = None,
        symbols: Optional[List[str]] = None,
        category_ids: Optional[List[str]] = None,
        sector_ids: Optional[List[str]] = None,
        industry_ids: Optional[List[str]] = None,
        api_sources: Optional[List[str]] = None,
        ticker_relevance: Optional[TickerRelevanceFilter] = None,
        exclude_list_articles: Optional[bool] = None,
        event_types: Optional[EventTypeFilter] = None,
        exclude_event_types: Optional[EventTypeFilter] = None,
        collapse_clusters: Optional[bool] = None,
    ) -> NewsStream:
        """Start streaming news updates.

        Args:
            locale: Locale code (e.g., "tr", "en")
            region: Region enum (e.g. Region.TR)
            lane: Optional lane filter. Lanes are region-scoped: US lanes are
                GLOBAL_MACRO and FAST_MOVERS; TR lanes are TR_EKONOMI and BIST.
            symbols: Optional list of ticker symbols (same param as filter-news)
            category_ids: Optional list of numeric category ids from
                :meth:`get_news_categories`
            sector_ids: Optional list of Laplace sector ids
            industry_ids: Optional list of Laplace industry ids
            api_sources: Optional list of source ids from
                :meth:`get_news_api_source_names`; only these sources are
                streamed
            ticker_relevance: Same as on :meth:`get_news_v2`
            exclude_list_articles: Same as on :meth:`get_news_v2`
            event_types: Same as on :meth:`get_news_v2`
            exclude_event_types: Same as on :meth:`get_news_v2`
            collapse_clusters: Same as on :meth:`get_news_v2`

        Returns:
            NewsStream for consuming news items
        """
        stream = NewsStream(
            self._client,
            locale,
            region,
            lane=lane,
            symbols=symbols,
            category_ids=category_ids,
            sector_ids=sector_ids,
            industry_ids=industry_ids,
            api_sources=api_sources,
            ticker_relevance=ticker_relevance,
            exclude_list_articles=exclude_list_articles,
            event_types=event_types,
            exclude_event_types=exclude_event_types,
            collapse_clusters=collapse_clusters,
        )
        await stream.subscribe()
        return stream
