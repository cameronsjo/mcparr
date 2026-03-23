"""FastMCP server with Streamable HTTP transport."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from servarr.config import Settings

logger = logging.getLogger("servarr")

# ---------------------------------------------------------------------------
# Lifespan — initialize clients, yield context, tear down
# ---------------------------------------------------------------------------


@lifespan
async def app_lifespan(server: FastMCP) -> dict[str, Any]:  # type: ignore[misc]
    """Initialize API clients for all enabled services."""
    settings = Settings()
    clients: dict[str, Any] = {}

    if settings.sonarr.enabled:
        from servarr.clients.sonarr import SonarrClient

        clients["sonarr"] = SonarrClient(settings.sonarr.url, settings.sonarr.api_key)

    if settings.radarr.enabled:
        from servarr.clients.radarr import RadarrClient

        clients["radarr"] = RadarrClient(settings.radarr.url, settings.radarr.api_key)

    if settings.prowlarr.enabled:
        from servarr.clients.prowlarr import ProwlarrClient

        clients["prowlarr"] = ProwlarrClient(settings.prowlarr.url, settings.prowlarr.api_key)

    if settings.sabnzbd.enabled:
        from servarr.clients.sabnzbd import SabnzbdClient

        clients["sabnzbd"] = SabnzbdClient(settings.sabnzbd.url, settings.sabnzbd.api_key)

    if settings.bazarr.enabled:
        from servarr.clients.bazarr import BazarrClient

        clients["bazarr"] = BazarrClient(settings.bazarr.url, settings.bazarr.api_key)

    enabled = list(clients.keys())
    logger.info("Servarr starting. Enabled services: %s", enabled)

    try:
        yield {"clients": clients, "settings": settings}
    finally:
        for name, client in clients.items():
            try:
                await client.close()
            except Exception:
                logger.warning("Failed to close %s client", name, exc_info=True)
        logger.info("Servarr shut down.")


# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "servarr",
    instructions=(
        "MCP server for managing the *arr media automation stack. "
        "Provides tools for Sonarr (TV), Radarr (movies), Prowlarr (indexers), "
        "SABnzbd (downloads), and Bazarr (subtitles). "
        "Use search tools to find content, queue tools to check download status, "
        "and calendar tools for upcoming releases."
    ),
    lifespan=app_lifespan,
)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "servarr"})


# ---------------------------------------------------------------------------
# System status tool (always registered)
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        openWorldHint=False,
    )
)
async def get_system_status(ctx: Any) -> dict[str, Any]:
    """Get health and version info for all configured *arr services.

    Returns the system status for each enabled service including version,
    uptime, and disk space.
    """
    clients: dict[str, Any] = ctx.lifespan_context["clients"]
    results: dict[str, Any] = {}

    for name, client in clients.items():
        try:
            status = await client.system_status()
            results[name] = {"status": "ok", **status}
        except Exception as exc:
            results[name] = {"status": "error", "error": str(exc)}

    return results


# ---------------------------------------------------------------------------
# Register per-service tools (only for enabled services)
# ---------------------------------------------------------------------------


def register_tools(settings: Settings) -> None:
    """Register tools for enabled services. Called during server startup."""
    if settings.sonarr.enabled:
        from servarr.tools.sonarr import register as register_sonarr

        register_sonarr(mcp)

    if settings.radarr.enabled:
        from servarr.tools.radarr import register as register_radarr

        register_radarr(mcp)

    if settings.prowlarr.enabled:
        from servarr.tools.prowlarr import register as register_prowlarr

        register_prowlarr(mcp)

    if settings.sabnzbd.enabled:
        from servarr.tools.sabnzbd import register as register_sabnzbd

        register_sabnzbd(mcp)

    if settings.bazarr.enabled:
        from servarr.tools.bazarr import register as register_bazarr

        register_bazarr(mcp)
