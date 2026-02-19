"""Search client for Laplace API."""

from typing import List, Optional

from laplace.base import BaseClient

from .models import (
    Region,
    SearchData,
    SearchType,
)


class SearchClient:
    """Client for search-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the search client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def search(
        self,
        filter: str,
        types: List[SearchType],
        region: Region,
        locale: str = "en",
        page: Optional[int] = None,
        size: Optional[int] = None,
    ) -> SearchData:
        """Search for stocks, sectors, industries, and collections.

        Args:
            filter: Search term
            types: Comma-separated list of types to search for (stock, sector, industry, collection)
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            SearchData: Search results containing stocks, collections, sectors, and industries
        """
        params = {
            "filter": filter,
            "types": ",".join([t.value for t in types]),
            "region": region.value,
            "locale": locale,
        }

        if page:
            params["page"] = page

        if size:
            params["size"] = size

        response = self._client.get("v1/search", params=params)
        return SearchData(**response)
