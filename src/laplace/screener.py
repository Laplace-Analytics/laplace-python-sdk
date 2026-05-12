"""Screener client for Laplace API."""

from typing import Optional

from laplace.base import BaseClient

from .models import (
    PaginatedResponse,
    Region,
    ScreenerFilters,
    ScreenerSortBy,
    ScreenerStock,
    SortDirection,
)


class ScreenerClient:
    """Client for the stock screener endpoint."""

    def __init__(self, base_client: BaseClient):
        self._client = base_client

    def screen(
        self,
        region: Region = Region.TR,
        filters: Optional[ScreenerFilters] = None,
        sort_by: Optional[ScreenerSortBy] = None,
        sort_order: Optional[SortDirection] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[ScreenerStock]:
        """Run the screener with optional filters, sorting, and pagination.

        Args:
            region: Region (only 'tr' is currently supported).
            filters: Optional filter ranges (price, P/E, returns, etc.).
            sort_by: Optional sort field.
            sort_order: Optional sort direction.
            page: Page number, 1-based (1-10000, default 1).
            page_size: Results per page (1-100, default 20).

        Returns:
            PaginatedResponse[ScreenerStock]
        """
        if region != Region.TR:
            raise ValueError("Screener endpoint only supports the 'tr' region")

        body: dict = {"page": page, "pageSize": page_size}

        if filters is not None:
            filters_body = filters.model_dump(by_alias=True, exclude_none=True)
            if filters_body:
                body["filters"] = filters_body
        if sort_by is not None:
            body["sortBy"] = sort_by.value
        if sort_order is not None:
            body["sortOrder"] = sort_order.value

        response = self._client._request(
            "POST",
            "v1/screener",
            params={"region": region.value},
            json=body,
        )
        return PaginatedResponse[ScreenerStock](**response)
