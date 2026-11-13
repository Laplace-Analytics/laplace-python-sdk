"""Tests for the v2 news additions: filters, ordering, cursors, new fields."""

import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import httpx
import pytest

from laplace import LaplaceClient
from laplace.base import LaplaceAPIError
from laplace.models import (
    NewsEventType,
    NewsEventTypeInfo,
    NewsOrderBy,
    NewsOriginality,
    NewsTickerRelevance,
    NewsV2,
    NewsV2Page,
    PaginatedResponse,
    PaginationPageSize,
    Region,
    SortDirection,
)

ITEM_ALL_FIELDS = {
    "id": "3f6c1e2a",
    "url": "https://www.ekonomim.com/a",
    "imageUrl": "https://x/image.jpg",
    "publisherUrl": "https://www.ekonomim.com",
    "publisher": {"name": "Ekonomim", "logoUrl": None},
    "publishedAt": None,
    "ingestedAt": "2026-11-12T10:24:13.106706Z",
    "contentUpdatedAt": None,
    "updatedAt": "2026-11-12T10:31:02.55192Z",
    "createdAt": "2026-11-12T10:24:13.106706Z",
    "timestamp": "2026-11-12T10:24:13.106706Z",
    "content": {
        "title": "THY ekim ayında 8,1 milyon yolcu taşıdı",
        "description": "d",
        "content": ["p"],
        "summary": ["s"],
        "investorInsight": "i",
    },
    "primaryTicker": "THYAO",
    "tickers": [
        {
            "id": "61dd0d6",
            "symbol": "THYAO",
            "name": "Türk Hava Yolları",
            "region": "tr",
            "relevance": "primary",
        }
    ],
    "isListArticle": False,
    "eventType": {"slug": "operational-data", "name": "Operasyonel Veriler", "language": "tr"},
    "qualityScore": 7,
    "clusterId": "9b1d",
    "isClusterLead": True,
    "clusterSize": 4,
    "originality": "original",
    "someFieldAddedLater": {"x": 1},
}

ITEM_OLD_SHAPE = {
    "id": "old",
    "url": "https://x/a",
    "imageUrl": "",
    "publisherUrl": "https://x",
    "publisher": {"name": "X"},
    "timestamp": "2025-01-02T03:04:05Z",
    "createdAt": "2025-01-02T03:04:05Z",
    "qualityScore": 5,
    "tickers": [{"id": "1", "name": "Apple", "symbol": "AAPL"}],
}


@pytest.fixture
def client():
    with patch("httpx.Client"):
        return LaplaceClient(api_key="test-key")


def call_v2(client, response=None, **kwargs):
    """Call get_news_v2 with a mocked ``get`` and return the query params sent."""
    response = response or {"recordCount": 0, "items": []}
    with patch.object(client, "get", return_value=response) as mock_get:
        result = client.news.get_news_v2(**kwargs)
    assert mock_get.call_args[0][0] == "v2/news"
    return mock_get.call_args[1]["params"], result


class TestNewsV2Query:
    def test_new_params_are_sent_with_api_names(self, client):
        params, _ = call_v2(
            client,
            locale="tr",
            region=Region.TR,
            symbols=["THYAO", "GARAN"],
            page_size=73,
            ticker_relevance=[NewsTickerRelevance.PRIMARY, "mentioned"],
            exclude_list_articles=False,
            event_types=[NewsEventType.DIVIDEND, "some-new-slug"],
            exclude_event_types="other",
            collapse_clusters=True,
            max_publisher_share=25,
            published_from="2026-11-01",
            published_to=datetime(2026, 11, 12, 9, 0),
            updated_since=datetime(2026, 11, 10, 3, 0, tzinfo=timezone.utc),
            as_of="2026-11-11T00:00:00Z",
            cursor="abc",
            include_total=False,
        )
        assert params == {
            "locale": "tr",
            "region": "tr",
            "size": 73,
            "symbols": "THYAO,GARAN",
            "tickerRelevance": "primary,mentioned",
            "excludeListArticles": "false",
            "eventTypes": "dividend,some-new-slug",
            "excludeEventTypes": "other",
            "collapseClusters": "true",
            "maxPublisherShare": 25,
            "publishedFrom": "2026-11-01",
            "publishedTo": "2026-11-12T09:00:00Z",
            "updatedSince": "2026-11-10T03:00:00Z",
            "asOf": "2026-11-11T00:00:00Z",
            "cursor": "abc",
            "includeTotal": "false",
        }

    def test_unset_params_are_not_sent(self, client):
        params, _ = call_v2(client, locale="en", region=Region.US)
        # page=0 and size=10 are what get_news_v2 always sent before.
        assert params == {"locale": "en", "region": "us", "page": 0, "size": 10}

    def test_page_is_omitted_with_cursor_and_kept_when_explicit(self, client):
        params, _ = call_v2(client, locale="en", region=Region.US, cursor="c")
        assert "page" not in params
        params, _ = call_v2(client, locale="en", region=Region.US, page=3)
        assert params["page"] == 3

    def test_page_size_accepts_enum_and_int(self, client):
        params, _ = call_v2(
            client, locale="en", region=Region.US, page_size=PaginationPageSize.PAGE_SIZE_50
        )
        assert params["size"] == 50
        params, _ = call_v2(client, locale="en", region=Region.US, page_size=100)
        assert params["size"] == 100


class TestNewsV2OrderBy:
    def test_single_field(self, client):
        params, _ = call_v2(
            client, locale="en", region=Region.US, news_order_by=NewsOrderBy.PUBLISHED_AT
        )
        assert params["orderBy"] == "publishedAt"
        assert "orderByDirection" not in params

    def test_single_field_with_direction(self, client):
        params, _ = call_v2(
            client,
            locale="en",
            region=Region.US,
            news_order_by=NewsOrderBy.UPDATED_AT,
            direction=SortDirection.ASC,
        )
        assert params["orderBy"] == "updatedAt"
        assert params["orderByDirection"] == "asc"

    def test_legacy_quality_score(self, client):
        params, _ = call_v2(
            client, locale="en", region=Region.US, news_order_by=NewsOrderBy.QUALITY_SCORE
        )
        assert params["orderBy"] == "quality_score"

    def test_multi_field(self, client):
        params, _ = call_v2(
            client,
            locale="en",
            region=Region.US,
            news_order_by=NewsOrderBy.TIMESTAMP,
            direction=SortDirection.ASC,
            order_by=[
                (NewsOrderBy.QUALITY_SCORE_V2, SortDirection.DESC),
                ("publishedAt", "desc"),
                NewsOrderBy.INGESTED_AT,
            ],
        )
        assert params["orderBy"] == "qualityScore desc,publishedAt desc,ingestedAt"
        assert "orderByDirection" not in params


class TestNewsV2Parsing:
    def test_item_with_all_new_fields(self):
        item = NewsV2(**ITEM_ALL_FIELDS)
        assert item.published_at is None
        assert item.content_updated_at is None
        assert item.ingested_at == datetime(2026, 11, 12, 10, 24, 13, 106706, tzinfo=timezone.utc)
        assert item.updated_at is not None
        assert item.primary_ticker == "THYAO"
        assert item.is_list_article is False
        assert item.event_type == NewsEventTypeInfo(
            slug="operational-data", name="Operasyonel Veriler", language="tr"
        )
        assert item.cluster_id == "9b1d"
        assert item.is_cluster_lead is True
        assert item.cluster_size == 4
        assert item.originality == NewsOriginality.ORIGINAL
        ticker = item.tickers[0]
        assert ticker.region == "tr"
        assert ticker.relevance == NewsTickerRelevance.PRIMARY
        assert ticker.name == "Türk Hava Yolları"

    def test_item_with_old_shape(self):
        item = NewsV2(**ITEM_OLD_SHAPE)
        assert item.id == "old"
        assert item.published_at is None
        assert item.ingested_at is None
        assert item.event_type is None
        assert item.is_list_article is False
        assert item.cluster_size is None
        assert item.publisher.logo_url is None
        assert item.tickers[0].relevance is None

    def test_page_with_null_record_count_cursor_and_publisher_cap(self, client):
        _, page = call_v2(
            client,
            {
                "recordCount": None,
                "items": [ITEM_ALL_FIELDS],
                "nextCursor": "c1",
                "publisherCap": {"share": 25, "perPublisher": 42, "achievedShare": 24.9},
            },
            locale="tr",
            region=Region.TR,
        )
        assert isinstance(page, NewsV2Page)
        assert isinstance(page, PaginatedResponse)
        assert page.record_count is None
        assert page.next_cursor == "c1"
        assert page.publisher_cap.share == 25
        assert page.publisher_cap.per_publisher == 42
        assert page.publisher_cap.achieved_share == 24.9
        assert page.items[0].primary_ticker == "THYAO"

    def test_page_with_old_shape(self, client):
        _, page = call_v2(client, {"recordCount": 549, "items": []}, locale="tr", region=Region.TR)
        assert page.record_count == 549
        assert page.next_cursor is None
        assert page.publisher_cap is None


class TestIterNewsV2:
    def test_follows_cursor_until_missing(self, client):
        pages = [
            {
                "recordCount": None,
                "items": [ITEM_OLD_SHAPE, ITEM_OLD_SHAPE],
                "nextCursor": "next-1",
            },
            {"recordCount": None, "items": [ITEM_ALL_FIELDS]},
        ]
        with patch.object(client, "get", side_effect=pages) as mock_get:
            ids = [
                n.id
                for n in client.news.iter_news_v2(
                    "tr",
                    Region.TR,
                    symbols="THYAO",
                    page_size=2,
                    event_types=[NewsEventType.DIVIDEND],
                )
            ]

        assert ids == ["old", "old", "3f6c1e2a"]
        assert mock_get.call_count == 2
        first, second = (c[1]["params"] for c in mock_get.call_args_list)
        for params in (first, second):
            assert params["symbols"] == "THYAO"
            assert params["size"] == 2
            assert params["eventTypes"] == "dividend"
            assert params["includeTotal"] == "false"
            assert "page" not in params
            assert "skip" not in params
        assert "cursor" not in first
        assert second["cursor"] == "next-1"

    def test_rejects_page(self, client):
        with pytest.raises(ValueError):
            next(client.news.iter_news_v2("tr", Region.TR, page=1))

    def test_stops_on_first_error(self, client):
        error = LaplaceAPIError("boom", status_code=400, response={"message": "invalid cursor"})
        pages = [{"recordCount": None, "items": [ITEM_OLD_SHAPE], "nextCursor": "n"}, error]
        with patch.object(client, "get", side_effect=pages):
            it = client.news.iter_news_v2("tr", Region.TR)
            assert next(it).id == "old"
            with pytest.raises(LaplaceAPIError) as exc:
                next(it)
        assert exc.value.response["message"] == "invalid cursor"


class TestNewsV2Errors:
    def test_validation_message_is_surfaced(self):
        message = 'invalid eventTypes value "foo": must be one of financial-results, guidance'

        def handler(request):
            assert request.url.params["eventTypes"] == "foo"
            return httpx.Response(400, json={"message": message, "error_code": "validation"})

        client = LaplaceClient(api_key="test-key")
        client._client = httpx.Client(transport=httpx.MockTransport(handler))
        with pytest.raises(LaplaceAPIError) as exc:
            client.news.get_news_v2(locale="tr", region=Region.TR, event_types=["foo"])
        assert exc.value.status_code == 400
        assert exc.value.response["message"] == message


class TestNewsEventTypes:
    def test_get_news_event_types(self, client):
        response = [
            {"slug": "financial-results", "name": "Finansal Sonuçlar", "language": "tr"},
            {"slug": "guidance", "name": "Beklenti ve Hedefler", "language": "tr"},
        ]
        with patch.object(client, "get", return_value=response) as mock_get:
            types = client.news.get_news_event_types(locale="tr")
        assert mock_get.call_args[0][0] == "v1/news/event-types"
        assert mock_get.call_args[1]["params"] == {"locale": "tr"}
        assert types[0].slug == NewsEventType.FINANCIAL_RESULTS
        assert types[0].name == "Finansal Sonuçlar"
        assert len(types) == 2

    def test_locale_is_optional(self, client):
        with patch.object(client, "get", return_value=[]) as mock_get:
            client.news.get_news_event_types()
        assert mock_get.call_args[1]["params"] == {}


class TestNewsStreamV2Filters:
    def test_stream_url_includes_new_filters(self):
        from laplace.base import BaseClient
        from laplace.news import NewsStream

        base = Mock(spec=BaseClient)
        base.base_url = "http://test-api.com"
        stream = NewsStream(
            base,
            "tr",
            Region.TR,
            symbols=["THYAO"],
            ticker_relevance=[NewsTickerRelevance.PRIMARY],
            exclude_list_articles=True,
            event_types=[NewsEventType.DIVIDEND, NewsEventType.GUIDANCE],
            exclude_event_types=["other"],
            collapse_clusters=False,
        )
        url = stream._build_stream_url()
        assert "tickerRelevance=primary" in url
        assert "excludeListArticles=true" in url
        assert "eventTypes=dividend%2Cguidance" in url
        assert "excludeEventTypes=other" in url
        assert "collapseClusters=false" in url

        url = NewsStream(base, "tr", Region.TR)._build_stream_url()
        for name in ("tickerRelevance", "excludeListArticles", "eventTypes", "collapseClusters"):
            assert name not in url

    @pytest.mark.asyncio
    async def test_stream_parses_new_fields(self):
        from laplace.base import BaseClient
        from laplace.news import NewsStream

        stream = NewsStream(Mock(spec=BaseClient), "tr", Region.TR)
        stream._queue = __import__("asyncio").Queue()

        class FakeResponse:
            async def aiter_lines(self):
                yield ": connected"
                yield "data: " + json.dumps([ITEM_ALL_FIELDS, ITEM_OLD_SHAPE])

        await stream._process_stream_lines(FakeResponse())
        result = stream._queue.get_nowait()
        assert result.error is None
        assert result.data[0].primary_ticker == "THYAO"
        assert result.data[1].event_type is None

    @pytest.mark.asyncio
    async def test_get_news_stream_forwards_new_filters(self, client):
        from unittest.mock import AsyncMock

        with patch("laplace.news.NewsStream.subscribe", new_callable=AsyncMock):
            stream = await client.news.get_news_stream(
                locale="tr",
                region=Region.TR,
                ticker_relevance=["primary"],
                exclude_list_articles=True,
                event_types=[NewsEventType.DIVIDEND],
                exclude_event_types=[NewsEventType.OTHER],
                collapse_clusters=True,
            )
        assert stream.ticker_relevance == ["primary"]
        assert stream.exclude_list_articles is True
        assert stream.event_types == [NewsEventType.DIVIDEND]
        assert stream.exclude_event_types == [NewsEventType.OTHER]
        assert stream.collapse_clusters is True


class TestNewsV2Integration:
    """Live API tests; skipped without LAPLACE_API_KEY."""

    @pytest.mark.integration
    def test_thyao_ticker_has_name(self, integration_client: LaplaceClient):
        page = integration_client.news.get_news_v2(
            locale="tr", region=Region.TR, symbols="THYAO", page_size=10
        )
        tickers = [t for item in page.items for t in (item.tickers or []) if t.symbol == "THYAO"]
        assert tickers, "no THYAO ticker in result"
        assert tickers[0].name

    @pytest.mark.integration
    def test_cursor_run_ends(self, integration_client: LaplaceClient):
        since = datetime.now(timezone.utc).date().isoformat()
        items = list(
            integration_client.news.iter_news_v2(
                "tr", Region.TR, symbols="THYAO", page_size=100, published_from=since
            )
        )
        assert all(isinstance(i, NewsV2) for i in items)

    @pytest.mark.integration
    def test_invalid_event_type_raises_with_api_message(self, integration_client: LaplaceClient):
        with pytest.raises(LaplaceAPIError) as exc:
            integration_client.news.get_news_v2(locale="tr", region=Region.TR, event_types=["foo"])
        assert exc.value.status_code == 400
        assert "eventTypes" in exc.value.response["message"]

    @pytest.mark.integration
    def test_event_types(self, integration_client: LaplaceClient):
        types = integration_client.news.get_news_event_types(locale="tr")
        assert types and types[0].slug and types[0].name
