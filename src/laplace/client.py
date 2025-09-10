"""Main Laplace client."""

from .base import BaseClient
from .brokers import BrokersClient
from .capital_increase import CapitalIncreaseClient
from .collections import CollectionsClient
from .earnings import EarningsClient
from .financials import FinancialsClient
from .funds import FundsClient
from .live_price import LivePriceClient
from .politician import PoliticianClient
from .search import SearchClient
from .state import StateClient
from .stocks import StocksClient
from .websocket import LivePriceWebSocketClient, LivePriceFeed, WebsocketOptions
from typing import Optional, List


class LaplaceClient(BaseClient):
    """Main Laplace API client with all sub-clients."""

    def __init__(self, api_key: str, base_url: str = "https://uat.api.finfree.app/api"):
        """Initialize the Laplace client.

        Args:
            api_key: Your Laplace API key
            base_url: Base URL for the API (default: https://api.finfree.app/api)
        """
        super().__init__(api_key, base_url)

        # Initialize sub-clients
        self.stocks = StocksClient(self)
        self.collections = CollectionsClient(self)
        self.financials = FinancialsClient(self)
        self.funds = FundsClient(self)
        self.live_price = LivePriceClient(self)
        self.politicians = PoliticianClient(self)
        self.brokers = BrokersClient(self)
        self.capital_increase = CapitalIncreaseClient(self)
        self.earnings = EarningsClient(self)
        self.search = SearchClient(self)
        self.state = StateClient(self)

        # WebSocket client will be created on demand
        self._websocket_client: Optional[LivePriceWebSocketClient] = None

    def create_websocket_client(
        self,
        feeds: List[LivePriceFeed],
        external_user_id: str,
        options: Optional[WebsocketOptions] = None,
    ) -> LivePriceWebSocketClient:
        """Create a WebSocket client for live price data.

        Args:
            feeds: List of feeds to subscribe to
            external_user_id: External user ID
            options: WebSocket configuration options

        Returns:
            WebSocket client instance
        """
        return LivePriceWebSocketClient(
            feeds=feeds,
            external_user_id=external_user_id,
            api_key=self.api_key,
            base_url=self.base_url,
            options=options,
        )
