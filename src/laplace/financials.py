"""Financials client for Laplace API."""

from typing import List

from .models import (
    Currency,
    FinancialSheetDate,
    FinancialSheetPeriod,
    FinancialSheetType,
    HistoricalFinancialSheets,
    RatioComparisonPeerType,
    StockHistoricalRatios,
    StockHistoricalRatiosDescription,
    StockPeerFinancialRatioComparison,
)


class FinancialsClient:
    """Client for financial data API endpoints."""

    def __init__(self, base_client):
        """Initialize the financials client.
        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_financial_ratio_comparison(
        self, symbol: str, region: str, peer_type: RatioComparisonPeerType
    ) -> List[StockPeerFinancialRatioComparison]:
        params = {
            "symbol": symbol,
            "region": region,
            "peerType": peer_type.value,
        }
        resp = self._client.get("v2/stock/financial-ratio-comparison", params=params)
        return [StockPeerFinancialRatioComparison(**item) for item in resp]

    def get_historical_ratios(
        self, symbol: str, keys: List[str], region: str, locale: str
    ) -> List[StockHistoricalRatios]:
        params = {
            "symbol": symbol,
            "region": region,
            "locale": locale,
            "slugs": ",".join(keys),
        }
        resp = self._client.get("v2/stock/historical-ratios", params=params)
        return [StockHistoricalRatios(**item) for item in resp]

    def get_historical_ratios_descriptions(
        self, locale: str, region: str
    ) -> List[StockHistoricalRatiosDescription]:
        params = {
            "locale": locale,
            "region": region,
        }
        resp = self._client.get("v2/stock/historical-ratios/descriptions", params=params)
        return [StockHistoricalRatiosDescription(**item) for item in resp]

    def get_historical_financial_sheets(
        self,
        symbol: str,
        from_date: FinancialSheetDate,
        to_date: FinancialSheetDate,
        sheet_type: FinancialSheetType,
        period: FinancialSheetPeriod,
        currency: Currency,
        region: str,
    ) -> HistoricalFinancialSheets:
        if (
            sheet_type == FinancialSheetType.BALANCE_SHEET
            and period != FinancialSheetPeriod.CUMULATIVE
        ):
            raise ValueError("balance sheet is only available for cumulative period")

        params = {
            "symbol": symbol,
            "from": f"{from_date.year:04d}-{from_date.month:02d}-{from_date.day:02d}",
            "to": f"{to_date.year:04d}-{to_date.month:02d}-{to_date.day:02d}",
            "sheetType": sheet_type.value,
            "periodType": period.value,
            "currency": currency.value,
            "region": region,
        }
        resp = self._client.get("v3/stock/historical-financial-sheets", params=params)
        return HistoricalFinancialSheets(**resp)
