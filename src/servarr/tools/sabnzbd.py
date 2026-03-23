"""MCP tools for SABnzbd download management."""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from servarr.clients.sabnzbd import SabnzbdClient


def register(mcp: FastMCP) -> None:
    """Register SABnzbd tools on the MCP server."""

    def _client(ctx: Context) -> SabnzbdClient:
        return ctx.lifespan_context["clients"]["sabnzbd"]

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        ),
    )
    async def get_downloads(ctx: Context) -> dict[str, Any]:
        """Get the current SABnzbd download queue.

        Returns download speed, total remaining size, estimated time left,
        and a list of active downloads with name, progress, size, status,
        category, and ETA.
        """
        queue = await _client(ctx).get_queue()
        downloads = [
            {
                "name": slot.get("filename", ""),
                "progress_pct": slot.get("percentage", "0"),
                "size": slot.get("size", ""),
                "size_left": slot.get("sizeleft", ""),
                "status": slot.get("status", ""),
                "category": slot.get("cat", ""),
                "eta": slot.get("timeleft", ""),
            }
            for slot in queue.get("slots", [])
        ]
        return {
            "speed": queue.get("speed", "0"),
            "total_size_left": queue.get("sizeleft", "0 B"),
            "time_left": queue.get("timeleft", "0:00:00"),
            "paused": queue.get("paused", False),
            "downloads": downloads,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=False,
        ),
    )
    async def get_download_history(
        ctx: Context,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get SABnzbd completed download history.

        Args:
            limit: Maximum number of history entries to return.
        """
        history = await _client(ctx).get_history(limit=limit)
        entries = [
            {
                "name": slot.get("name", ""),
                "status": slot.get("status", ""),
                "size": slot.get("size", ""),
                "completed": slot.get("completed", 0),
                "category": slot.get("category", ""),
            }
            for slot in history.get("slots", [])
        ]
        return {
            "total_items": history.get("noofslots", 0),
            "entries": entries,
        }

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def pause_downloads(
        ctx: Context,
        minutes: int | None = None,
    ) -> dict[str, str]:
        """Pause the SABnzbd download queue.

        Args:
            minutes: Optional duration in minutes. Omit to pause indefinitely.
        """
        await _client(ctx).pause(minutes=minutes)
        if minutes is not None:
            return {"message": f"Downloads paused for {minutes} minutes."}
        return {"message": "Downloads paused."}

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def resume_downloads(ctx: Context) -> dict[str, str]:
        """Resume the SABnzbd download queue."""
        await _client(ctx).resume()
        return {"message": "Downloads resumed."}
