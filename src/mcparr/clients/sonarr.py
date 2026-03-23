"""Sonarr API v3 client for TV series management."""

from __future__ import annotations

from typing import Any

from mcparr.clients.base import BaseArrClient


class SonarrClient(BaseArrClient):
    """Client for the Sonarr TV series management API (v3)."""

    service_name = "sonarr"

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__(base_url, api_key, api_version="v3")

    async def search_series(self, term: str) -> list[dict[str, Any]]:
        """Search for TV series by name via Sonarr's lookup endpoint."""
        return await self.get("series/lookup", params={"term": term})

    async def get_all_series(self) -> list[dict[str, Any]]:
        """Get all series currently in the Sonarr library."""
        return await self.get("series")

    async def get_series(self, series_id: int) -> dict[str, Any]:
        """Get detailed info for a specific series by its Sonarr ID."""
        return await self.get(f"series/{series_id}")

    async def add_series(
        self,
        tvdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        season_folder: bool = True,
    ) -> dict[str, Any]:
        """Add a new series to Sonarr and trigger a search for missing episodes."""
        return await self.post(
            "series",
            json={
                "tvdbId": tvdb_id,
                "title": title,
                "qualityProfileId": quality_profile_id,
                "rootFolderPath": root_folder_path,
                "monitored": monitored,
                "seasonFolder": season_folder,
                "addOptions": {"searchForMissingEpisodes": True},
            },
        )

    async def get_queue(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Get the current download queue with episode details."""
        return await self.get(
            "queue",
            params={
                "page": page,
                "pageSize": page_size,
                "includeEpisode": "true",
            },
        )

    async def get_calendar(
        self, start: str | None = None, end: str | None = None
    ) -> list[dict[str, Any]]:
        """Get upcoming episodes within a date range (ISO 8601 dates)."""
        params: dict[str, str] = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("calendar", params=params or None)

    async def get_root_folders(self) -> list[dict[str, Any]]:
        """Get configured root folders for series storage."""
        return await self.get("rootfolder")

    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        """Get available quality profiles."""
        return await self.get("qualityprofile")
