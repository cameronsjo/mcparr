"""MCP tool definitions for Sonarr TV series management."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from mcparr.clients.sonarr import SonarrClient


def _get_client(ctx: Context) -> SonarrClient:
    """Extract the Sonarr client from lifespan context."""
    return ctx.lifespan_context["clients"]["sonarr"]


def register(mcp: FastMCP) -> None:
    """Register Sonarr tools on the MCP server."""

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    async def search_series(ctx: Context, query: str) -> list[dict[str, Any]]:
        """Search for TV series by name. Searches the Sonarr lookup database
        and existing library.

        Returns series with title, year, season count, episode count, and
        whether the series is already in your library.
        """
        client = _get_client(ctx)
        results = await client.search_series(query)
        return [
            {
                "title": s.get("title"),
                "year": s.get("year"),
                "tvdb_id": s.get("tvdbId"),
                "status": s.get("status"),
                "season_count": s.get("statistics", {}).get("seasonCount", 0),
                "episode_count": s.get("statistics", {}).get("totalEpisodeCount", 0),
                "monitored": s.get("monitored"),
                "in_library": s.get("id") is not None and s.get("id", 0) > 0,
            }
            for s in results
        ]

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    async def get_series(ctx: Context, series_id: int) -> dict[str, Any]:
        """Get detailed information for a specific TV series by its Sonarr ID.

        Returns title, year, status, path, quality profile, network, genres,
        runtime, ratings, and a per-season breakdown of episode counts and
        monitored status.
        """
        client = _get_client(ctx)
        data = await client.get_series(series_id)
        stats = data.get("statistics", {})
        seasons = [
            {
                "season_number": season.get("seasonNumber"),
                "monitored": season.get("monitored"),
                "episode_count": season.get("statistics", {}).get("totalEpisodeCount", 0),
                "episode_file_count": season.get("statistics", {}).get("episodeFileCount", 0),
                "percent_of_episodes": season.get("statistics", {}).get("percentOfEpisodes", 0),
            }
            for season in data.get("seasons", [])
        ]
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "year": data.get("year"),
            "status": data.get("status"),
            "path": data.get("path"),
            "quality_profile_id": data.get("qualityProfileId"),
            "network": data.get("network"),
            "genres": data.get("genres", []),
            "runtime": data.get("runtime"),
            "rating": data.get("ratings", {}).get("value"),
            "monitored": data.get("monitored"),
            "season_count": stats.get("seasonCount", 0),
            "total_episode_count": stats.get("totalEpisodeCount", 0),
            "episode_file_count": stats.get("episodeFileCount", 0),
            "size_on_disk": stats.get("sizeOnDisk", 0),
            "seasons": seasons,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            openWorldHint=False,
        ),
    )
    async def add_series(
        ctx: Context,
        tvdb_id: int,
        quality_profile_id: int | None = None,
        root_folder_path: str | None = None,
    ) -> dict[str, Any]:
        """Add a TV series to Sonarr by its TVDB ID and start downloading.

        Use search_series first to find the tvdb_id. Quality profile and root
        folder are optional -- if not provided, the first available profile and
        root folder from Sonarr's configuration are used.
        """
        client = _get_client(ctx)

        # Look up series metadata from TVDB so Sonarr gets the full record
        lookup = await client.search_series(f"tvdb:{tvdb_id}")
        if not lookup:
            return {"error": f"No series found for TVDB ID {tvdb_id}"}
        series_data = lookup[0]
        title = series_data.get("title", "Unknown")

        # Resolve defaults for optional parameters
        if quality_profile_id is None:
            profiles = await client.get_quality_profiles()
            if not profiles:
                return {"error": "No quality profiles configured in Sonarr"}
            quality_profile_id = profiles[0]["id"]

        if root_folder_path is None:
            folders = await client.get_root_folders()
            if not folders:
                return {"error": "No root folders configured in Sonarr"}
            root_folder_path = folders[0]["path"]

        result = await client.add_series(
            tvdb_id=tvdb_id,
            title=title,
            quality_profile_id=quality_profile_id,
            root_folder_path=root_folder_path,
        )
        return {
            "id": result.get("id"),
            "title": result.get("title"),
            "year": result.get("year"),
            "path": result.get("path"),
            "quality_profile_id": result.get("qualityProfileId"),
            "monitored": result.get("monitored"),
            "added": result.get("added"),
        }

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    async def get_series_queue(ctx: Context) -> dict[str, Any]:
        """Get the current TV series download queue from Sonarr.

        Returns active downloads with series/episode info, progress percentage,
        estimated time remaining, and download status.
        """
        client = _get_client(ctx)
        data = await client.get_queue()
        records = data.get("records", [])
        items = []
        for record in records:
            episode = record.get("episode", {})
            size = record.get("size", 0)
            size_left = record.get("sizeleft", 0)
            progress = round((1 - size_left / size) * 100, 1) if size > 0 else 0.0
            items.append(
                {
                    "series_title": record.get("title"),
                    "episode_title": episode.get("title"),
                    "season": episode.get("seasonNumber"),
                    "episode": episode.get("episodeNumber"),
                    "quality": record.get("quality", {}).get("quality", {}).get("name"),
                    "status": record.get("status"),
                    "progress_percent": progress,
                    "time_left": record.get("timeleft"),
                    "download_client": record.get("downloadClient"),
                }
            )
        return {
            "total_records": data.get("totalRecords", 0),
            "items": items,
        }

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    async def get_series_calendar(ctx: Context, days_ahead: int = 7) -> list[dict[str, Any]]:
        """Get upcoming TV episode releases from Sonarr.

        Returns episodes airing within the specified number of days, including
        series name, season/episode numbers, title, and air date.
        """
        client = _get_client(ctx)
        now = datetime.now(UTC)
        start = now.strftime("%Y-%m-%d")
        end = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        episodes = await client.get_calendar(start=start, end=end)
        return [
            {
                "series_title": ep.get("series", {}).get("title"),
                "season": ep.get("seasonNumber"),
                "episode": ep.get("episodeNumber"),
                "title": ep.get("title"),
                "air_date_utc": ep.get("airDateUtc"),
                "has_file": ep.get("hasFile", False),
                "monitored": ep.get("monitored"),
            }
            for ep in episodes
        ]
