"""Bazarr API client for subtitle management."""

from __future__ import annotations

from typing import Any

from servarr.clients.base import BaseArrClient


class BazarrClient(BaseArrClient):
    """Client for the Bazarr subtitle management API.

    Bazarr uses X-Api-Key auth like the *arr apps but has its own API
    structure with paths like /api/movies, /api/episodes (no version prefix).
    """

    service_name = "bazarr"

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__(base_url, api_key, api_version="")

    async def get_wanted_movies(self, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        """Get movies with missing subtitles."""
        return await self.get(
            "movies/wanted",
            params={"page": page, "pagesize": page_size},
        )

    async def get_wanted_episodes(self, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        """Get episodes with missing subtitles."""
        return await self.get(
            "episodes/wanted",
            params={"page": page, "pagesize": page_size},
        )

    async def search_movie_subtitles(self, radarr_id: int) -> dict[str, Any]:
        """Trigger a subtitle search for a movie by its Radarr ID."""
        return await self.post(
            "movies/subtitles",
            json={"radarrid": radarr_id},
        )

    async def search_episode_subtitles(self, sonarr_episode_id: int) -> dict[str, Any]:
        """Trigger a subtitle search for an episode by its Sonarr episode ID."""
        return await self.post(
            "episodes/subtitles",
            json={"sonarrepisodeid": sonarr_episode_id},
        )

    async def system_status(self) -> dict[str, Any]:
        """Get Bazarr system status."""
        return await self.get("system/status")
