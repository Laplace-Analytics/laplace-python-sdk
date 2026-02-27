"""Collections client for Laplace API."""

from typing import Dict, List, Optional

from laplace.base import BaseClient

from .models import (
    Collection,
    CollectionDetail,
    CollectionStatus,
    Locale,
    Region
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

    def get_themes(self, region: Region, locale: Locale = "en") -> List[Collection]:
        """Retrieve a list of themes along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Collection]: List of themes
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/theme", params=params)
        return [Collection(**theme) for theme in response]

    def get_theme_detail(self, theme_id: str, region: Region, locale: Locale = "en") -> CollectionDetail:
        """Retrieve detailed information about a specific theme.

        Args:
            theme_id: Unique identifier for the theme
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            CollectionDetail: Detailed theme information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/theme/{theme_id}", params=params)
        return CollectionDetail(**response)

    def get_industries(self, region: Region, locale: Locale = "en") -> List[Collection]:
        """Retrieve a list of industries along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Collection]: List of industries
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/industry", params=params)
        return [Collection(**industry) for industry in response]

    def get_industry_detail(
        self, industry_id: str, region: Region, locale: Locale = "en"
    ) -> CollectionDetail:
        """Retrieve detailed information about a specific industry.

        Args:
            industry_id: Unique identifier for the industry
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            CollectionDetail: Detailed industry information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/industry/{industry_id}", params=params)
        return CollectionDetail(**response)

    def get_custom_themes(self, locale: Locale, region: Region) -> List[Collection]:
        """Get a list of all your custom themes.

        Args:
            locale: Locale code (tr, en)
            region: Region code (tr, us)

        Returns:
            List[Collection]: List of custom themes
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get("v1/custom-theme", params=params)
        return [Collection(**theme) for theme in response]

    def get_custom_theme_detail(
        self, theme_id: str, locale: Locale, region: Region, sort_by: Optional[str] = None
    ) -> CollectionDetail:
        """Retrieve detailed information about a specific custom theme.

        Args:
            theme_id: Unique identifier for the custom theme
            locale: Locale code (tr, en)
            region: Region code (tr, us)
            sort_by: Sort the stocks by a specific field (e.g., "price_change") (optional)

        Returns:
            CollectionDetail: Detailed custom theme information
        """
        params = {"locale": locale, "region": region.value}

        if sort_by:
            params["sortBy"] = sort_by

        response = self._client.get(f"v1/custom-theme/{theme_id}", params=params)
        return CollectionDetail(**response)

    def delete_custom_theme(self, theme_id: str) -> None:
        """Delete specific custom theme.

        Args:
            theme_id: Unique identifier for the custom theme
        """
        self._client.delete(f"v1/custom-theme/{theme_id}")

    def create_custom_theme(
        self,
        title: Dict[str, str],
        stock_ids: List[str],
        status: CollectionStatus,
        description: Optional[Dict[str, str]] = None,
        region: Optional[List[Region]] = None,
        image_url: Optional[str] = None,
        image: Optional[str] = None,
        avatar_url: Optional[str] = None,
        order: Optional[int] = None,
        meta_data: Optional[dict] = None,
    ) -> str:
        """Create a new custom theme.

        Args:
            title: Localized title (e.g., {"tr": "Başlık", "en": "Title"})
            stock_ids: List of stock IDs
            status: Collection status
            description: Localized description (optional)
            region: List of regions (optional)
            image_url: Image URL (optional)
            image: Image data (optional)
            avatar_url: Avatar URL (optional)
            order: Display order (optional)
            meta_data: Additional metadata (optional)

        Returns:
            str: Created theme ID
        """
        body: dict = {
            "title": title,
            "stocks": stock_ids,
            "status": status.value,
        }

        if description is not None:
            body["description"] = description
        if region is not None:
            body["region"] = [r.value for r in region]
        if image_url is not None:
            body["image_url"] = image_url
        if image is not None:
            body["image"] = image
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        if order is not None:
            body["order"] = order
        if meta_data is not None:
            body["meta_data"] = meta_data

        response = self._client.post("v1/custom-theme", json=body)
        return response["id"]

    def update_custom_theme(
        self,
        theme_id: str,
        title: Optional[Dict[str, str]] = None,
        stock_ids: Optional[List[str]] = None,
        status: Optional[CollectionStatus] = None,
        description: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
        image: Optional[str] = None,
        avatar_url: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> None:
        """Update an existing custom theme.

        Args:
            theme_id: Unique identifier for the custom theme
            title: Localized title (optional)
            stock_ids: List of stock IDs (optional)
            status: Collection status (optional)
            description: Localized description (optional)
            image_url: Image URL (optional)
            image: Image data (optional)
            avatar_url: Avatar URL (optional)
            meta_data: Additional metadata (optional)
        """
        body: dict = {}

        if title is not None:
            body["title"] = title
        if stock_ids is not None:
            body["stockIds"] = stock_ids
        if status is not None:
            body["status"] = status.value
        if description is not None:
            body["description"] = description
        if image_url is not None:
            body["image_url"] = image_url
        if image is not None:
            body["image"] = image
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        if meta_data is not None:
            body["meta_data"] = meta_data

        self._client.patch(f"v1/custom-theme/{theme_id}", json=body)

    def get_sectors(self, region: Region, locale: Locale = "en") -> List[Collection]:
        """Retrieve a list of sectors along with the number of stocks in each.

        Args:
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            List[Collection]: List of sectors
        """
        params = {"region": region.value, "locale": locale}

        response = self._client.get("v1/sector", params=params)
        return [Collection(**sector) for sector in response]

    def get_sector_detail(
        self, sector_id: str, region: Region, locale: Locale = "en"
    ) -> CollectionDetail:
        """Retrieve detailed information about a specific sector.

        Args:
            sector_id: Unique identifier for the sector
            region: Region code (tr, us)
            locale: Locale code (tr, en) (default: en)

        Returns:
            CollectionDetail: Detailed sector information
        """
        params = {"locale": locale, "region": region.value}

        response = self._client.get(f"v1/sector/{sector_id}", params=params)
        return CollectionDetail(**response)
