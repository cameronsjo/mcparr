"""MCP tools for Bazarr subtitle management."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations


def register(mcp: FastMCP) -> None:
    """Register Bazarr tools on the MCP server."""

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        )
    )
    async def get_wanted_subtitles(ctx: Context) -> dict[str, Any]:
        """Get movies and episodes that are missing subtitles.

        Returns a combined list of movies and episodes with missing subtitle
        languages, along with their Radarr/Sonarr IDs for triggering searches.
        """
        client = ctx.lifespan_context["clients"]["bazarr"]

        movies_resp = await client.get_wanted_movies()
        episodes_resp = await client.get_wanted_episodes()

        movies_data = (
            movies_resp.get("data", movies_resp) if isinstance(movies_resp, dict) else movies_resp
        )
        episodes_data = (
            episodes_resp.get("data", episodes_resp)
            if isinstance(episodes_resp, dict)
            else episodes_resp
        )

        wanted: list[dict[str, Any]] = []

        if isinstance(movies_data, list):
            for movie in movies_data:
                wanted.append(
                    {
                        "type": "movie",
                        "title": movie.get("title", "Unknown"),
                        "radarr_id": movie.get("radarrId"),
                        "missing_languages": movie.get("missing_subtitles", []),
                    }
                )

        if isinstance(episodes_data, list):
            for episode in episodes_data:
                wanted.append(
                    {
                        "type": "episode",
                        "title": episode.get("seriesTitle", episode.get("title", "Unknown")),
                        "season": episode.get("season"),
                        "episode": episode.get("episode"),
                        "sonarr_episode_id": episode.get("sonarrEpisodeId"),
                        "missing_languages": episode.get("missing_subtitles", []),
                    }
                )

        movie_count = (
            movies_resp.get("total", 0)
            if isinstance(movies_resp, dict)
            else sum(1 for w in wanted if w["type"] == "movie")
        )
        episode_count = (
            episodes_resp.get("total", 0)
            if isinstance(episodes_resp, dict)
            else sum(1 for w in wanted if w["type"] == "episode")
        )

        return {
            "total_movies": movie_count,
            "total_episodes": episode_count,
            "wanted": wanted,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
            openWorldHint=True,
        )
    )
    async def search_subtitles(
        ctx: Context,
        media_type: Literal["movie", "episode"],
        media_id: int,
    ) -> dict[str, Any]:
        """Trigger a subtitle search for a movie or episode.

        Searches configured external subtitle providers (OpenSubtitles, etc.)
        for matching subtitles.

        Args:
            media_type: "movie" for Radarr movies, "episode" for Sonarr episodes.
            media_id: Radarr ID for movies, Sonarr episode ID for episodes.
        """
        client = ctx.lifespan_context["clients"]["bazarr"]

        if media_type == "movie":
            result = await client.search_movie_subtitles(media_id)
        else:
            result = await client.search_episode_subtitles(media_id)

        return {
            "media_type": media_type,
            "media_id": media_id,
            "result": result,
        }
