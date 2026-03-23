"""Radarr API v3 client for movie management."""

from __future__ import annotations

from typing import Any

from servarr.clients.base import BaseArrClient


class RadarrClient(BaseArrClient):
    """Client for the Radarr movie management API (v3)."""

    service_name = "radarr"

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__(base_url, api_key, api_version="v3")

    async def search_movies(self, term: str) -> list[dict[str, Any]]:
        """Search for movies by title via TMDb lookup."""
        return await self.get("movie/lookup", params={"term": term})

    async def get_all_movies(self) -> list[dict[str, Any]]:
        """Get all movies in the Radarr library."""
        return await self.get("movie")

    async def get_movie(self, movie_id: int) -> dict[str, Any]:
        """Get a single movie by its Radarr database ID."""
        return await self.get(f"movie/{movie_id}")

    async def add_movie(
        self,
        tmdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
    ) -> dict[str, Any]:
        """Add a movie to Radarr and trigger a search for it."""
        return await self.post(
            "movie",
            json={
                "tmdbId": tmdb_id,
                "title": title,
                "qualityProfileId": quality_profile_id,
                "rootFolderPath": root_folder_path,
                "monitored": monitored,
                "addOptions": {"searchForMovie": True},
            },
        )

    async def get_queue(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Get the movie download queue with progress info."""
        return await self.get(
            "queue",
            params={"page": page, "pageSize": page_size, "includeMovie": "true"},
        )

    async def get_calendar(
        self, start: str | None = None, end: str | None = None
    ) -> list[dict[str, Any]]:
        """Get upcoming movie releases within a date range.

        Args:
            start: ISO 8601 date string for range start.
            end: ISO 8601 date string for range end.
        """
        params: dict[str, str] = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("calendar", params=params or None)

    async def get_root_folders(self) -> list[dict[str, Any]]:
        """Get configured root folders for movie storage."""
        return await self.get("rootfolder")

    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        """Get available quality profiles."""
        return await self.get("qualityprofile")
