"""Earnings client for Laplace API."""

from typing import List
from laplace.base import BaseClient
from .models import (
    Region,
    EarningsTranscriptListItem,
    EarningsTranscriptWithSummary,
)


class EarningsClient:
    """Client for earnings-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the earnings client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_transcripts(
        self, symbol: str, region: Region = Region.US
    ) -> List[EarningsTranscriptListItem]:
        """Retrieve earnings transcripts for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            region: Region code (only 'us' is supported) (default: us)

        Returns:
            List[EarningsTranscriptListItem]: List of earnings transcripts
        """
        if region != Region.US:
            raise ValueError("Earnings transcripts endpoint only works with the 'us' region")

        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v1/earnings/transcript", params=params)
        return [EarningsTranscriptListItem(**data) for data in response]

    def get_transcript_with_summary(
        self, symbol: str, year: int, quarter: int
    ) -> EarningsTranscriptWithSummary:
        """Retrieve earnings transcript with summary for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            year: Year (2000-2050)
            quarter: Quarter (1-4)

        Returns:
            EarningsTranscriptWithSummary: Earnings transcript with summary data
        """
        if not 2000 <= year <= 2050:
            raise ValueError("Year must be between 2000 and 2050")

        if not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")

        params = {"symbol": symbol, "year": year, "quarter": quarter}

        response = self._client.get("v1/earnings/transcript/summary", params=params)
        return EarningsTranscriptWithSummary(**response)
