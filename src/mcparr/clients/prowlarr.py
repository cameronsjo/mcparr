"""Prowlarr API v1 client for indexer management and search."""

from __future__ import annotations

from typing import Any

from mcparr.clients.base import BaseArrClient


class ProwlarrClient(BaseArrClient):
    """Client for the Prowlarr indexer management API (v1)."""

    service_name = "prowlarr"

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__(base_url, api_key, api_version="v1")

    async def search(
        self,
        query: str,
        categories: list[int] | None = None,
        indexer_ids: list[int] | None = None,
    ) -> list[dict[str, Any]]:
        """Search across configured indexers.

        Args:
            query: Search term.
            categories: Newznab category IDs (2000=Movies, 5000=TV, 3000=Audio, 7000=Books).
            indexer_ids: Limit search to specific indexer IDs.
        """
        params: dict[str, Any] = {"query": query}
        if categories:
            params["categories"] = categories
        if indexer_ids:
            params["indexerIds"] = indexer_ids
        return await self.get("search", params=params)

    async def get_indexers(self) -> list[dict[str, Any]]:
        """Get all configured indexers."""
        return await self.get("indexer")

    async def get_indexer_stats(self) -> dict[str, Any]:
        """Get performance statistics for all indexers."""
        return await self.get("indexerstats")
