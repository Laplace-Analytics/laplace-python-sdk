"""Laplace Intelligence client for Laplace API."""

from laplace.base import BaseClient


class LaplaceIntelligenceClient:
    """Client for Laplace Intelligence API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the Laplace Intelligence client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client
