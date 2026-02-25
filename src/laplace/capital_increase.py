"""Capital Increase client for Laplace API."""

from datetime import datetime
from typing import List, Optional
from laplace.base import BaseClient

from .models import (
    Region,
    CapitalIncrease,
    PaginatedResponse,
    PaginationPageSize,
)


class CapitalIncreaseClient:
    """Client for capital increase and rights-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the capital increase client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all(
        self,
        region: Region = Region.TR,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[CapitalIncrease]:
        """Retrieve all capital increases.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            PaginatedResponse[CapitalIncrease]: Capital increase data
        """
        if region != Region.TR:
            raise ValueError("Capital increase endpoint only works with the 'tr' region")

        params = {"region": region.value, "page": page, "size": size.value}

        response = self._client.get("v1/capital-increase/all", params=params)
        return PaginatedResponse[CapitalIncrease](**response)

    def get_by_symbol(
        self,
        symbol: str,
        region: Region = Region.TR,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[CapitalIncrease]:
        """Retrieve capital increase information by ID.

        Args:
            symbol: Stock symbol (e.g., "AKBNK")
            region: Region code (only 'tr' is supported) (default: tr)
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            PaginatedResponse[CapitalIncrease]: Capital increase information
        """
        if region != Region.TR:
            raise ValueError("Capital increase endpoint only works with the 'tr' region")

        params = {"region": region.value, "page": page, "size": size.value}

        response = self._client.get(f"v1/capital-increase/{symbol}", params=params)
        return PaginatedResponse[CapitalIncrease](**response)

    def get_active_rights(self, symbol: str, date: Optional[datetime] = None) -> List[CapitalIncrease]:
        """Retrieve active rights for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AKBNK")
            date: Optional date filter (defaults to today on the server)

        Returns:
            List[CapitalIncrease]: Active rights data
        """
        params = {}

        if date is not None:
            params["date"] = date.strftime("%Y-%m-%d")

        response = self._client.get(f"v1/rights/active/{symbol}", params=params)

        return [CapitalIncrease(**item) for item in response]
