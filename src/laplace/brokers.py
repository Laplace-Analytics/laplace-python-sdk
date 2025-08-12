"""Brokers client for Laplace API."""

from datetime import datetime
from typing import List

from laplace.base import BaseClient

from .models import (
    PaginationPageSize,
    Region,
    BrokerTradingData,
    BrokerMarketData,
    BrokerStockData,
    BrokerSortDirection,
    BrokerSort,
)


class BrokersClient:
    """Client for broker-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the brokers client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all(self, region: Region = Region.TR) -> List[BrokerTradingData]:
        """Retrieve all brokers.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            List[BrokerTradingData]: List of brokers
        """
        if region != Region.TR:
            raise ValueError("Brokers endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get("v1/brokers", params=params)
        return [BrokerTradingData(**item) for item in response["items"]]

    def get_by_symbol(self, symbol: str, region: Region = Region.TR) -> BrokerTradingData:
        """Retrieve broker information by symbol.

        Args:
            symbol: Broker symbol (e.g., "BIMLB")
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            BrokerTradingData: Broker information
        """
        if region != Region.TR:
            raise ValueError("Broker endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get(f"v1/brokers/{symbol}", params=params)
        return BrokerTradingData(**response)

    def get_market_data(
        self,
        region: Region,
        sort_by: BrokerSort,
        sort_direction: BrokerSortDirection,
        from_date: datetime,
        to_date: datetime,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> BrokerMarketData:
        """Retrieve broker market data.

        Args:
            region: Region code (only 'tr' is supported)
            sort_by: Sort by field (netAmount, totalAmount, totalVolume, etc.)
            sort_direction: Sort direction (asc, desc)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            BrokerMarketData: Broker market data
        """
        if region != Region.TR:
            raise ValueError("Broker market endpoint only works with the 'tr' region")

        params = {
            "region": region.value,
            "sortBy": sort_by.value,
            "sortDirection": sort_direction.value,
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d"),
            "page": page,
            "size": size.value,
        }

        response = self._client.get("v1/brokers/market", params=params)
        return BrokerMarketData(**response)

    def get_stock_data(
        self,
        symbol: str,
        region: Region,
        sort_by: BrokerSort,
        sort_direction: BrokerSortDirection,
        from_date: datetime,
        to_date: datetime,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> BrokerStockData:
        """Retrieve stock data for a specific broker.

        Args:
            symbol: Broker symbol (e.g., "BIMLB")
            region: Region code (only 'tr' is supported)
            sort_by: Sort by field (netAmount, totalAmount, totalVolume, etc.)
            sort_direction: Sort direction (asc, desc)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            BrokerStockData: Stock data for the broker
        """
        if region != Region.TR:
            raise ValueError("Broker stock endpoint only works with the 'tr' region")

        params = {
            "region": region.value,
            "sortBy": sort_by.value,
            "sortDirection": sort_direction.value,
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d"),
            "page": page,
            "size": size.value,
        }

        response = self._client.get(f"v1/brokers/stock/{symbol}", params=params)
        return BrokerStockData(**response)

    def get_market_stock_data(
        self,
        region: Region,
        sort_by: BrokerSort,
        sort_direction: BrokerSortDirection,
        from_date: datetime,
        to_date: datetime,
        page: int = 0,
        size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> BrokerStockData:
        """Retrieve market stock data for brokers.

        Args:
            region: Region code (only 'tr' is supported)
            sort_by: Sort by field (netAmount, totalAmount, totalVolume, etc.)
            sort_direction: Sort direction (asc, desc)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            page: Page number (default: 0)
            size: Page size (default: 10)

        Returns:
            BrokerStockData: Market stock data for brokers
        """
        if region != Region.TR:
            raise ValueError("Broker market stock endpoint only works with the 'tr' region")

        params = {
            "region": region.value,
            "sortBy": sort_by.value,
            "sortDirection": sort_direction.value,
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d"),
            "page": page,
            "size": size.value,
        }

        response = self._client.get("v1/brokers/market/stock", params=params)
        return BrokerStockData(**response)
