"""MCP tools for Radarr movie management."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from servarr.clients.radarr import RadarrClient


def _get_client(ctx: Context) -> RadarrClient:
    """Extract the Radarr client from lifespan context."""
    return ctx.lifespan_context["clients"]["radarr"]


def register(mcp: FastMCP) -> None:
    """Register Radarr tools on the MCP server."""

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        )
    )
    async def search_movies(term: str, ctx: Context) -> list[dict[str, Any]]:
        """Search for movies by title.

        Searches TMDb via Radarr and shows whether each result is already
        in your library. Use this before add_movie to find the tmdb_id.

        Args:
            term: Movie title or partial title to search for.
        """
        client = _get_client(ctx)
        results = await client.search_movies(term)
        library = {m["tmdbId"] for m in await client.get_all_movies()}

        return [
            {
                "title": m.get("title", ""),
                "year": m.get("year"),
                "tmdb_id": m.get("tmdbId"),
                "overview": (m.get("overview") or "")[:200],
                "in_library": m.get("tmdbId") in library,
                "runtime": m.get("runtime"),
                "studio": m.get("studio", ""),
            }
            for m in results
        ]

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        )
    )
    async def get_movie(movie_id: int, ctx: Context) -> dict[str, Any]:
        """Get detailed info about a movie in Radarr by its database ID.

        Includes file information if the movie has been downloaded.

        Args:
            movie_id: The Radarr internal movie ID.
        """
        client = _get_client(ctx)
        m = await client.get_movie(movie_id)

        result: dict[str, Any] = {
            "id": m.get("id"),
            "title": m.get("title", ""),
            "year": m.get("year"),
            "tmdb_id": m.get("tmdbId"),
            "overview": m.get("overview", ""),
            "monitored": m.get("monitored"),
            "status": m.get("status"),
            "runtime": m.get("runtime"),
            "studio": m.get("studio", ""),
            "quality_profile_id": m.get("qualityProfileId"),
            "root_folder_path": m.get("rootFolderPath", ""),
            "has_file": m.get("hasFile", False),
            "size_on_disk": m.get("sizeOnDisk", 0),
        }

        movie_file = m.get("movieFile")
        if movie_file:
            result["file"] = {
                "relative_path": movie_file.get("relativePath", ""),
                "size": movie_file.get("size", 0),
                "quality": movie_file.get("quality", {}).get("quality", {}).get("name", ""),
                "date_added": movie_file.get("dateAdded", ""),
            }

        return result

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=False,
            openWorldHint=False,
        )
    )
    async def add_movie(
        tmdb_id: int,
        ctx: Context,
        quality_profile_id: int | None = None,
        root_folder_path: str | None = None,
    ) -> dict[str, Any]:
        """Add a movie to Radarr by its TMDb ID.

        Triggers an automatic search for the movie after adding. Use
        search_movies first to find the tmdb_id.

        If quality_profile_id or root_folder_path are omitted, the first
        available profile and root folder are used as defaults.

        Args:
            tmdb_id: The Movie Database (TMDb) ID for the movie.
            quality_profile_id: Radarr quality profile ID. Uses first available if omitted.
            root_folder_path: Storage path for downloads. Uses first configured folder if omitted.
        """
        client = _get_client(ctx)

        # Resolve defaults when not provided
        if quality_profile_id is None:
            profiles = await client.get_quality_profiles()
            if not profiles:
                return {"error": "No quality profiles configured in Radarr."}
            quality_profile_id = profiles[0]["id"]

        if root_folder_path is None:
            folders = await client.get_root_folders()
            if not folders:
                return {"error": "No root folders configured in Radarr."}
            root_folder_path = folders[0]["path"]

        # Look up movie metadata from TMDb via Radarr
        lookup = await client.search_movies(f"tmdb:{tmdb_id}")
        if not lookup:
            return {"error": f"Movie not found for TMDb ID {tmdb_id}."}

        title = lookup[0].get("title", "Unknown")

        added = await client.add_movie(
            tmdb_id=tmdb_id,
            title=title,
            quality_profile_id=quality_profile_id,
            root_folder_path=root_folder_path,
        )

        return {
            "id": added.get("id"),
            "title": added.get("title", ""),
            "year": added.get("year"),
            "tmdb_id": added.get("tmdbId"),
            "monitored": added.get("monitored"),
            "quality_profile_id": added.get("qualityProfileId"),
            "root_folder_path": added.get("rootFolderPath", ""),
            "added": True,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        )
    )
    async def get_movie_queue(ctx: Context) -> dict[str, Any]:
        """Get the current movie download queue.

        Shows all movies currently being downloaded with progress,
        status, and estimated time remaining.
        """
        client = _get_client(ctx)
        queue = await client.get_queue()
        records = queue.get("records", [])

        items = []
        for r in records:
            movie = r.get("movie", {})
            size = r.get("size", 0)
            remaining = r.get("sizeleft", 0)
            progress = round((1 - remaining / size) * 100, 1) if size > 0 else 0.0

            items.append(
                {
                    "title": movie.get("title", "Unknown"),
                    "year": movie.get("year"),
                    "status": r.get("status", ""),
                    "progress_pct": progress,
                    "size_mb": round(size / 1_048_576, 1),
                    "time_left": r.get("timeleft", ""),
                    "quality": r.get("quality", {}).get("quality", {}).get("name", ""),
                    "indexer": r.get("indexer", ""),
                }
            )

        return {
            "total_records": queue.get("totalRecords", 0),
            "items": items,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        )
    )
    async def get_movie_calendar(
        days_ahead: int = 30,
        ctx: Context = None,  # type: ignore[assignment]
    ) -> list[dict[str, Any]]:
        """Get upcoming movie releases.

        Shows movies with physical or digital releases in the upcoming
        period. Movies release less frequently than TV episodes, so the
        default window is 30 days.

        Args:
            days_ahead: Number of days to look ahead. Default 30.
        """
        client = _get_client(ctx)
        now = datetime.now(tz=UTC)
        start = now.strftime("%Y-%m-%d")
        end = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        movies = await client.get_calendar(start=start, end=end)

        return [
            {
                "title": m.get("title", ""),
                "year": m.get("year"),
                "tmdb_id": m.get("tmdbId"),
                "physical_release": m.get("physicalRelease", ""),
                "digital_release": m.get("digitalRelease", ""),
                "in_cinemas": m.get("inCinemas", ""),
                "status": m.get("status", ""),
                "monitored": m.get("monitored"),
                "has_file": m.get("hasFile", False),
            }
            for m in movies
        ]
