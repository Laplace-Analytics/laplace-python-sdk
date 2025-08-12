"""State client for Laplace API."""

from typing import List

from laplace.base import BaseClient

from .models import (
    Region,
    MarketState,
    PaginatedResponse,
    PaginationPageSize,
)


class StateClient(BaseClient):
    """Client for state-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the state client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all_market_states(
        self,
        region: Region = Region.TR,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[MarketState]:
        """Retrieve all market states.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)
            page: Page number (default: 0)
            page_size: Page size (default: 10)

        Returns:
            PaginatedResponse: Paginated response with market states
        """
        if region != Region.TR:
            raise ValueError("State endpoint only works with the 'tr' region")

        params = {"region": region.value, "page": page, "size": page_size.value}

        response = self._client.get("v1/state/all", params=params)
        return PaginatedResponse[MarketState](**response)

    def get_market_state(self, symbol: str, region: Region = Region.TR) -> MarketState:
        """Retrieve market state information by symbol.

        Args:
            symbol: Market symbol
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            MarketState: Market state information
        """
        if region != Region.TR:
            raise ValueError("State endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get(f"v1/state/{symbol}", params=params)
        return MarketState(**response)

    def get_all_stock_states(
        self,
        region: Region = Region.TR,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> PaginatedResponse[MarketState]:
        """Retrieve all stock states.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)
            page: Page number (default: 0)
            page_size: Page size (default: 10)

        Returns:
            PaginatedResponse: Paginated response with stock states
        """
        if region != Region.TR:
            raise ValueError("State stock all endpoint only works with the 'tr' region")

        params = {"region": region.value, "page": page, "size": page_size.value}

        response = self._client.get("v1/state/stock/all", params=params)
        return PaginatedResponse[MarketState](**response)

    def get_stock_state(self, symbol: str, region: Region = Region.TR) -> MarketState:
        """Retrieve stock state information by symbol.

        Args:
            symbol: Stock symbol
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            MarketState: Stock state information
        """
        if region != Region.TR:
            raise ValueError("State stock endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get(f"v1/state/stock/{symbol}", params=params)
        return MarketState(**response)
