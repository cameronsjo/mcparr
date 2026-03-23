"""MCP tools for Prowlarr indexer management and search."""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from mcparr.clients.prowlarr import ProwlarrClient

# Newznab standard category mapping
CATEGORY_MAP: dict[str, int] = {
    "movies": 2000,
    "tv": 5000,
    "audio": 3000,
    "books": 7000,
}


def register(mcp: FastMCP) -> None:
    """Register Prowlarr tools on the MCP server."""

    def _client(ctx: Context) -> ProwlarrClient:
        return ctx.lifespan_context["clients"]["prowlarr"]

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=True,
        ),
    )
    async def search_indexers(
        ctx: Context,
        query: str,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Search across all Prowlarr indexers for releases.

        Searches configured Usenet and torrent indexers. Results include
        release title, indexer name, size, age, and torrent-specific info
        (seeders/leechers) when applicable.

        Args:
            query: Search term (movie title, show name, etc.).
            category: Optional content category filter. One of: movies, tv, audio, books.
        """
        categories: list[int] | None = None
        if category:
            category_id = CATEGORY_MAP.get(category.lower())
            if category_id is None:
                valid = ", ".join(sorted(CATEGORY_MAP))
                return {"error": f"Unknown category '{category}'. Valid: {valid}"}
            categories = [category_id]

        results = await _client(ctx).search(query, categories=categories)
        releases = [
            {
                "title": r.get("title", ""),
                "indexer": r.get("indexer", ""),
                "size_mb": round(r.get("size", 0) / 1_048_576, 1),
                "age_days": r.get("age", 0),
                "seeders": r.get("seeders"),
                "leechers": r.get("leechers"),
                "grab_url": r.get("downloadUrl") or r.get("guid", ""),
                "category": r.get("categories", [{}])[0].get("name", "")
                if r.get("categories")
                else "",
            }
            for r in results
        ]
        return {
            "query": query,
            "category": category,
            "total_results": len(releases),
            "releases": releases,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        ),
    )
    async def get_indexer_stats(ctx: Context) -> dict[str, Any]:
        """Get performance statistics for all Prowlarr indexers.

        Returns per-indexer success/failure counts and average response times.
        Useful for identifying unreliable or slow indexers.
        """
        stats = await _client(ctx).get_indexer_stats()
        indexers = [
            {
                "name": idx.get("indexerName", ""),
                "queries": idx.get("numberOfQueries", 0),
                "grabs": idx.get("numberOfGrabs", 0),
                "failed_queries": idx.get("numberOfFailedQueries", 0),
                "failed_grabs": idx.get("numberOfFailedGrabs", 0),
                "avg_response_ms": round(idx.get("averageResponseTime", 0)),
            }
            for idx in stats.get("indexers", [])
        ]
        return {
            "indexer_count": len(indexers),
            "indexers": indexers,
        }
