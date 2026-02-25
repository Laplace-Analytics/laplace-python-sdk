"""Stocks client for Laplace API."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from laplace.base import BaseClient

from .models import (
    AssetType,
    Locale,
    PriceCandle,
    Region,
    Stock,
    StockDetail,
    StockPriceData,
    StockRestriction,
    StockRules,
    TopMover,
    Dividend,
    StockStats,
    AggregateGraphData,
    KeyInsight,
    PaginationPageSize,
    AssetClass,
)


class IntervalPrice(Enum):
    """Interval price options."""

    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"


class HistoricalPriceInterval(Enum):
    """Historical price interval options."""

    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"
    THREE_MONTH = "3M"
    ONE_YEAR = "1Y"
    TWO_YEAR = "2Y"
    THREE_YEAR = "3Y"


class StocksClient:
    """Client for stock-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the stocks client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime to API required format: YYYY-MM-DD HH:MM:SS"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def get_all(
        self,
        region: Region,
        page: int = 1,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> List[Stock]:
        """Retrieve a list of all stocks available in the specified region.

        Args:
            region: Region code (tr, us)
            page: Page number (default: 1)
            page_size: Page size (default: 10)

        Returns:
            List[Stock]: List of stocks
        """
        params = {"page": page, "pageSize": page_size.value, "region": region.value}

        response = self._client.get("v2/stock/all", params=params)
        return [Stock(**stock) for stock in response]

    def get_detail_by_id(self, stock_id: str, locale: Locale = "en") -> StockDetail:
        """Retrieve detailed information about a specific stock using its unique identifier.

        Args:
            stock_id: Unique identifier for the stock
            locale: Locale code (tr, en) (default: en)

        Returns:
            StockDetail: Detailed stock information
        """
        params = {"locale": locale}
        response = self._client.get(f"v1/stock/{stock_id}", params=params)
        return StockDetail(**response)

    def get_detail_by_symbol(
        self,
        symbol: str,
        region: Region,
        asset_class: AssetClass = AssetClass.EQUITY,
        locale: Locale = "en",
    ) -> StockDetail:
        """Retrieve detailed information about a specific stock using its symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            region: Region code (tr, us)
            asset_class: Asset class (equity, stock) (default: equity)
            locale: Locale code (tr, en) (default: en)

        Returns:
            StockDetail: Detailed stock information
        """
        params = {
            "locale": locale,
            "symbol": symbol,
            "region": region.value,
            "asset_class": asset_class.value,
        }

        response = self._client.get("v1/stock/detail", params=params)
        return StockDetail(**response)

    def get_price(
        self, region: Region, symbols: List[str], keys: List[str]
    ) -> List[StockPriceData]:
        """Retrieve the historical price of stocks in a specified region.

        Args:
            region: Region code (tr, us)
            symbols: List of stock symbols
            keys: List of time periods for which data is required.
                  Allowable values: 1D, 1W, 1M, 3M, 1Y, 5Y

        Returns:
            List[StockPriceData]: List of stock price data
        """
        params = {
            "region": region.value,
            "symbols": ",".join(symbols),
            "keys": ",".join(keys),
        }

        response = self._client.get("v1/stock/price", params=params)
        return [StockPriceData(**stock_data) for stock_data in response]

    def get_price_with_interval(
        self,
        symbol: str,
        region: Region,
        from_date: datetime,
        to_date: datetime,
        interval: Union[IntervalPrice, str],
        detail: bool = False,
        num_intervals: Optional[int] = None
    ) -> List[PriceCandle]:
        """Retrieve the historical price of a stock with custom date range and interval.

        Args:
            symbol: Stock symbol or stock ID
            region: Region code (tr, us)
            from_date: Start date and time
            to_date: End date and time
            interval: Price interval (use HistoricalPriceInterval enum or string)

        Returns:
            List[PriceCandle]: List of price candles
        """
        interval_value = interval.value if isinstance(interval, IntervalPrice) else interval

        params = {
            "stock": symbol,
            "region": region.value,
            "fromDate": self._format_datetime(from_date),
            "toDate": self._format_datetime(to_date),
            "interval": interval_value,
            "detail": detail
        }

        if num_intervals:
            params["numIntervals"] = num_intervals

        response = self._client.get("v1/stock/price/interval", params=params)
        return [PriceCandle(**candle) for candle in response]

    def get_tick_rules(self, symbol: str, region: Region = Region.TR) -> StockRules:
        """Retrieve the tick rules for creating orderbook and price limits.

        Note: This endpoint only works with the "tr" region.

        Args:
            region: Region code (must be "tr")

        Returns:
            StockRules: Tick rules and price limits
        """
        if region != Region.TR:
            raise ValueError("Tick rules endpoint only works with the 'tr' region")

        params = {"region": region.value, "symbol": symbol}
        response = self._client.get("v1/stock/rules", params=params)
        return StockRules(**response)

    def get_restrictions(self, symbol, region: Region = Region.TR) -> List[StockRestriction]:
        """Retrieve the restrictions for a stock.

        Note: This endpoint only works with the "tr" region.

        Args:
            region: Region code (must be "tr")

        Returns:
            List[StockRestriction]: List of stock restrictions
        """
        if region != Region.TR:
            raise ValueError("Restrictions endpoint only works with the 'tr' region")

        params = {"region": region.value, "symbol": symbol}
        response = self._client.get("v1/stock/restrictions", params=params)
        return [StockRestriction(**restriction) for restriction in response]

    def get_all_restrictions(self, region: Region = Region.TR) -> List[StockRestriction]:
        """Retrieve the active restrictions for all stocks.

        Note: This endpoint only works with the "tr" region.

        Args:
            region: Region code (must be "tr")

        Returns:
            List[StockRestriction]: List of all stock restrictions
        """
        if region != Region.TR:
            raise ValueError("All restrictions endpoint only works with the 'tr' region")

        params = {"region": region.value}
        response = self._client.get("v1/stock/restrictions/all", params=params)
        return [StockRestriction(**restriction) for restriction in response]

    def get_top_movers(
        self,
        region: Region,
        direction: str = "gainers",
        asset_type: AssetType = AssetType.STOCK,
        asset_class: AssetClass = AssetClass.EQUITY,
        page: int = 0,
        page_size: PaginationPageSize = PaginationPageSize.PAGE_SIZE_10,
    ) -> List[TopMover]:
        """Retrieve top movers for a specific region.

        Args:
            region: Region code (tr, us)
            direction: Direction of movers (gainers, losers) (default: gainers)
            page: Page number (default: 0)
            page_size: Page size (default: 10)

        Returns:
            List[TopMover]: List of top movers
        """
        params = {
            "region": region.value,
            "direction": direction,
            "page": page,
            "pageSize": page_size.value,
            "assetType": asset_type.value,
            "assetClass": asset_class.value
        }

        response = self._client.get("v2/stock/top-movers", params=params)
        return [TopMover(**mover) for mover in response]

    def get_dividends(self, symbol: str, region: Region) -> List[Dividend]:
        """Retrieve dividends for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            region: Region code (tr, us)

        Returns:
            List[Dividend]: List of dividends
        """
        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v2/stock/dividends", params=params)
        return [Dividend(**dividend) for dividend in response]

    def get_stats(self, symbols: List[str], region: Region) -> List[StockStats]:
        """Retrieve stats for specific stocks.

        Args:
            symbols: List of stock symbols (e.g., ["AAPL", "MSFT"])
            region: Region code (tr, us)

        Returns:
            List[StockStats]: List of stock stats
        """
        params = {"symbols": ",".join(symbols), "region": region.value}

        response = self._client.get("v2/stock/stats", params=params)
        return [StockStats(**stats) for stats in response]

    def get_aggregate_graph(
        self,
        region: Region,
        period: str,
        sector_id: Optional[str] = None,
        industry_id: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> AggregateGraphData:
        """Retrieve aggregate graph data.

        Args:
            region: Region code (tr, us)
            period: Period to aggregate over (1G, 1H, 1A, 3A, 1Y, 2Y, 3Y, 5Y)
            sector_id: Sector ID (optional)
            industry_id: Industry ID (optional)
            collection_id: Collection ID (optional)

        Returns:
            AggregateGraphData: Aggregate graph data
        """
        params = {"region": region.value, "period": period}

        if sector_id:
            params["sectorId"] = sector_id
        if industry_id:
            params["industryId"] = industry_id
        if collection_id:
            params["collectionId"] = collection_id

        response = self._client.get("v1/aggregate/graph", params=params)
        return AggregateGraphData(**response)

    def get_key_insight(self, symbol: str, region: Region) -> KeyInsight:
        """Retrieve key insights for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            region: Region code (tr, us)

        Returns:
            KeyInsight: Key insights data
        """
        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v1/key-insights", params=params)
        return KeyInsight(**response)

    def get_chart_image(
        self,
        symbol: str,
        region: Region = Region.TR,
        period: Optional[str] = None,
        resolution: Optional[str] = None,
        indicators: Optional[List[str]] = None,
        chart_type: Optional[int] = None,
    ) -> bytes:
        """Retrieve a chart image (PNG) for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AKBNK")
            region: Region code (default: tr)
            period: Chart period (1D, 1W, 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, All)
            resolution: Price resolution (1m, 3m, 5m, 15m, 30m, 1h, 2h, 1d, 5d, 7d, 30d)
            indicators: List of indicator names
            chart_type: Chart type (0-16, 19)

        Returns:
            bytes: PNG image data
        """
        params = {"symbol": symbol, "region": region.value}

        if period is not None:
            params["period"] = period
        if resolution is not None:
            params["resolution"] = resolution
        if indicators is not None:
            params["indicators"] = ",".join(indicators)
        if chart_type is not None:
            params["chartType"] = chart_type

        return self._client.get_bytes("v1/stock/chart", params=params)
