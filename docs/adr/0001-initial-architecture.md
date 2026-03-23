# ADR 0001: Initial Architecture

## Status

Accepted

## Date

2026-03-23

## Context

We need an MCP server that provides Claude with tools for managing the full \*arr media automation stack (Sonarr, Radarr, Prowlarr, SABnzbd, Bazarr). The previous `mcp-servarr` (from bdfrost) only covered Radarr/Sonarr and was non-functional.

## Decision

- **Python + FastMCP** for the server framework (Streamable HTTP transport)
- **httpx** async clients instead of pyarr — thinner dependency, full control
- **BaseArrClient** shared base for Sonarr/Radarr/Prowlarr/Bazarr (common API lineage)
- **Standalone SabnzbdClient** for SABnzbd's CGI-style API
- **Conditional tool registration** — unconfigured services don't register tools
- **Action-oriented tool design** — "search_movies" not "radarr_get_movie_endpoint"
- **Deployed behind agentgateway** on the mcp-net Docker network

## Consequences

- Adding a new \*arr service requires: a client in `clients/`, tools in `tools/`, config in `config.py`, and wiring in `server.py`
- No pyarr dependency means we own the API surface — easier to debug, harder to keep up with API changes
- Conditional registration keeps the tool list clean but means tools can appear/disappear based on env config
