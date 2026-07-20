"""IPO (halka arz) client for Laplace API."""

from laplace.base import BaseClient

from .models import (
    Region,
    HalkaArz,
    PaginatedResponse,
    PaginationPageSize,
)


class HalkaArzClient:
    """Client for IPO (halka arz) API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the halka arz client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all(
        self,
        region: Region = Region.TR,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[HalkaArz]:
        """Retrieve all IPO (halka arz) offerings.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            PaginatedResponse[HalkaArz]: IPO offering data
        """
        if region != Region.TR:
            raise ValueError("IPO endpoint only works with the 'tr' region")

        params = {"region": region.value, "page": page, "size": size.value}

        response = self._client.get("v1/ipo/all", params=params)
        return PaginatedResponse[HalkaArz](**response)

    def get_by_id(self, id: int) -> HalkaArz:
        """Retrieve a single IPO (halka arz) offering by its id.

        Args:
            id: The offering id

        Returns:
            HalkaArz: IPO offering data
        """
        response = self._client.get(f"v1/ipo/{id}")
        return HalkaArz(**response)
