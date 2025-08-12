"""State client for Laplace API."""

from typing import List

from laplace.base import BaseClient

from .models import Region


class StateClient(BaseClient):
    """Client for state-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the state client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_all(self, region: Region = Region.TR) -> List[dict]:
        """Retrieve all states.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            List[dict]: List of states
        """
        if region != Region.TR:
            raise ValueError("State endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get("v1/state/all", params=params)
        return response

    def get_by_id(self, state_id: str, region: Region = Region.TR) -> dict:
        """Retrieve state information by ID.

        Args:
            state_id: State ID
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            dict: State information
        """
        if region != Region.TR:
            raise ValueError("State endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get(f"v1/state/{state_id}", params=params)
        return response

    def get_stock_data(self, state_id: str, region: Region = Region.TR) -> List[dict]:
        """Retrieve stock data for a specific state.

        Args:
            state_id: State ID
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            List[dict]: Stock data for the state
        """
        if region != Region.TR:
            raise ValueError("State stock endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get(f"v1/state/stock/{state_id}", params=params)
        return response

    def get_all_stock_data(self, region: Region = Region.TR) -> List[dict]:
        """Retrieve all stock data for all states.

        Args:
            region: Region code (only 'tr' is supported) (default: tr)

        Returns:
            List[dict]: All stock data for all states
        """
        if region != Region.TR:
            raise ValueError("State stock all endpoint only works with the 'tr' region")

        params = {"region": region.value}

        response = self._client.get("v1/state/stock/all", params=params)
        return response
