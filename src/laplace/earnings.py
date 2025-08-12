"""Earnings client for Laplace API."""

from typing import List

from laplace.base import BaseClient

from .models import Region


class EarningsClient:
    """Client for earnings-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the earnings client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_transcripts(self, symbol: str, region: Region) -> List[dict]:
        """Retrieve earnings transcripts for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            region: Region code (tr, us)

        Returns:
            List[dict]: List of earnings transcripts
        """
        params = {"symbol": symbol, "region": region.value}

        response = self._client.get("v1/earnings/transcripts", params=params)
        return response

    def get_transcript(self, transcript_id: str, region: Region) -> dict:
        """Retrieve a specific earnings transcript.

        Args:
            transcript_id: Transcript ID
            region: Region code (tr, us)

        Returns:
            dict: Earnings transcript data
        """
        params = {"region": region.value}

        response = self._client.get(f"v1/earnings/transcript/{transcript_id}", params=params)
        return response
