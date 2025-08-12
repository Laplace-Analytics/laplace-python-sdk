"""Funds client for Laplace API."""

from typing import List

from laplace.base import BaseClient

from .models import (
    Fund,
    FundStats,
    FundPriceData,
    FundDistribution,
    Region,
    PaginationPageSize,
)


class FundsClient(BaseClient):
    """Client for fund-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the funds client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all(
        self,
        region: Region = Region.TR,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> List[Fund]:
        """Retrieve all funds.

        Args:
            region: Region code (default: tr)
            page: Page number (default: 0)
            page_size: Page size (default: 10)

        Returns:
            List[Fund]: List of funds
        """
        params = {"region": region.value, "page": page, "pageSize": page_size.value}

        response = self._client.get("v1/fund", params=params)
        return [Fund(**data) for data in response]

    def get_stats(self, symbol: str, region: Region = Region.TR) -> FundStats:
        """Retrieve stats for a TEFAS fund.

        Args:
            symbol: Fund symbol (e.g., "AFA")
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            FundStats: Fund statistics
        """
        if region != Region.TR:
            raise ValueError("Fund stats endpoint only works with the 'tr' region")

        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v1/fund/stats", params=params)
        return FundStats(**response)

    def get_price(
        self, symbol: str, period: str, region: Region = Region.TR
    ) -> List[FundPriceData]:
        """Retrieve historical price data for a TEFAS fund.

        Args:
            symbol: Fund symbol (e.g., "AFA")
            period: Period (1H, 1A, 3A, 1Y, 3Y, 5Y)
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            List[FundPriceData]: List of fund price data
        """
        if region != Region.TR:
            raise ValueError("Fund price endpoint only works with the 'tr' region")

        params = {"symbol": symbol, "period": period, "region": region.value}

        response = self._client.get("v1/fund/price", params=params)
        return [FundPriceData(**data) for data in response]

    def get_distribution(self, symbol: str, region: Region = Region.TR) -> FundDistribution:
        """Retrieve distribution data for a TEFAS fund.

        Args:
            symbol: Fund symbol (e.g., "AFA")
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            FundDistribution: Fund distribution data
        """
        if region != Region.TR:
            raise ValueError("Fund distribution endpoint only works with the 'tr' region")

        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v1/fund/distribution", params=params)
        return FundDistribution(**response)
