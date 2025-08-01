from typing import List
from laplace.models import Holding, Politician, PoliticianDetail, TopHolding


class PoliticianClient:
    def __init__(self, base_client):
        """Initialize the politician client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_politicians(self) -> List[Politician]:
        """Get all politicians.

        Returns:
            List[Politician]: A list of all politicians
        """

        response = self._client.get("v1/politician")
        return [Politician(**politician) for politician in response]

    def get_politician_holdings_by_symbol(self, symbol: str) -> List[Holding]:
        """Get all holdings for a specific politician.

        Args:
            symbol: The symbol of the politician

        Returns:
            List[Holding]: A list of all holdings for the politician
        """

        response = self._client.get(f"v1/holding/{symbol}")
        return [Holding(**holding) for holding in response]

    def get_top_holdings(self) -> List[TopHolding]:
        """Get all top holdings.

        Returns:
            List[TopHolding]: A list of all top holdings
        """

        response = self._client.get("v1/top-holding")
        return [TopHolding(**top_holding) for top_holding in response]

    def get_politician_detail(self, id: int) -> PoliticianDetail:
        """Get detailed information for a specific politician.

        Args:
            id: The id of the politician

        Returns:
            PoliticianDetail: Detailed information for the politician
        """

        response = self._client.get(f"v1/politician/{id}")
        return PoliticianDetail(**response)
