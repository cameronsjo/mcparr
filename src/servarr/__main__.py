"""Entry point for running the servarr MCP server."""

from __future__ import annotations

import logging
import sys

from servarr.config import Settings
from servarr.server import mcp, register_tools


def main() -> None:
    settings = Settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    register_tools(settings)

    mcp.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
        path=settings.path,
    )


if __name__ == "__main__":
    main()
