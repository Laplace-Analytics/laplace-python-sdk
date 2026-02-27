from typing import Dict, Optional

from laplace.base import BaseClient

from .models import (
    Locale,
    News,
    NewsHighlight,
    NewsOrderBy,
    NewsType,
    PaginatedResponse,
    Region,
    PaginationPageSize,
    SortDirection,
)


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
        extraFilters: Optional[str] = None,
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
            extraFilters: Optional extra filters (API-specific)
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
        if extraFilters:
            params["extraFilters"] = extraFilters

        response = self._client.get("v1/news", params=params)
        return PaginatedResponse[News](**response)

    def get_highlights(
        self,
        locale: Locale,
        region: Region
    ) -> NewsHighlight:
        """Retrieve paginated news.

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
