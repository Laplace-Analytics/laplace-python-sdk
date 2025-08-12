"""Collections client for Laplace API."""

from typing import List, Optional

from laplace.base import BaseClient

from .models import (
    Collection,
    CollectionDetail,
    Industry,
    IndustryDetail,
    Locale,
    Region,
    Sector,
    SectorDetail,
    Theme,
    ThemeDetail,
)


class CollectionsClient:
    """Client for collection-related API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize the collections client.

        Args:
            base_client: The base Laplace client instance
        """
        self._client = base_client

    def get_collections(self, region: Region, locale: Locale = "en") -> List[Collection]:
        """Get all collections in a specific region.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Collection]: List of collections
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/collection", params=params)
        return [Collection(**collection) for collection in response]

    def get_collection_detail(
        self, collection_id: str, region: Region, locale: Locale = "en"
    ) -> CollectionDetail:
        """Retrieve detailed information about a specific collection by its ID.

        Args:
            collection_id: Unique identifier for the collection
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            CollectionDetail: Detailed collection information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/collection/{collection_id}", params=params)
        return CollectionDetail(**response)

    def get_themes(self, region: Region, locale: Locale = "en") -> List[Theme]:
        """Retrieve a list of themes along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Theme]: List of themes
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/theme", params=params)
        return [Theme(**theme) for theme in response]

    def get_theme_detail(self, theme_id: str, region: Region, locale: Locale = "en") -> ThemeDetail:
        """Retrieve detailed information about a specific theme.

        Args:
            theme_id: Unique identifier for the theme
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            ThemeDetail: Detailed theme information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/theme/{theme_id}", params=params)
        return ThemeDetail(**response)

    def get_industries(self, region: Region, locale: Locale = "en") -> List[Industry]:
        """Retrieve a list of industries along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Industry]: List of industries
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/industry", params=params)
        return [Industry(**industry) for industry in response]

    def get_industry_detail(
        self, industry_id: str, region: Region, locale: Locale = "en"
    ) -> IndustryDetail:
        """Retrieve detailed information about a specific industry.

        Args:
            industry_id: Unique identifier for the industry
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            IndustryDetail: Detailed industry information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/industry/{industry_id}", params=params)
        return IndustryDetail(**response)

    def get_custom_themes(self, locale: Locale, region: Region) -> List[dict]:
        """Get a list of all your custom themes.

        Args:
            locale: Locale code (tr, en)
            region: Region code (tr, us)

        Returns:
            List[dict]: List of custom themes
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get("v1/custom-theme", params=params)
        return response

    def get_custom_theme_detail(
        self, theme_id: str, locale: Locale, region: Region, sort_by: Optional[str] = None
    ) -> dict:
        """Retrieve detailed information about a specific custom theme.

        Args:
            theme_id: Unique identifier for the custom theme
            locale: Locale code (tr, en)
            region: Region code (tr, us)
            sort_by: Sort the stocks by a specific field (e.g., "price_change") (optional)

        Returns:
            dict: Detailed custom theme information
        """
        params = {"locale": locale, "region": region.value}

        if sort_by:
            params["sortBy"] = sort_by

        response = self._client.get(f"v1/custom-theme/{theme_id}", params=params)
        return response

    def get_sectors(self, region: Region, locale: Locale = "en") -> List[Sector]:
        """Retrieve a list of sectors along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Sector]: List of sectors
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/sector", params=params)
        return [Sector(**sector) for sector in response]

    def get_sector_detail(
        self, sector_id: str, region: Region, locale: Locale = "en"
    ) -> SectorDetail:
        """Retrieve detailed information about a specific sector.

        Args:
            sector_id: Unique identifier for the sector
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            SectorDetail: Detailed sector information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/sector/{sector_id}", params=params)
        return SectorDetail(**response)
