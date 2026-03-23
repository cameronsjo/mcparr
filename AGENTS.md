# mcparr

Unified MCP server for the \*arr media automation stack. Provides 19 action-oriented tools across Sonarr, Radarr, Prowlarr, SABnzbd, and Bazarr via the Model Context Protocol.

## Stack

- **Language:** Python 3.12+
- **Framework:** FastMCP (Streamable HTTP transport)
- **HTTP Client:** httpx (async)
- **Config:** Pydantic Settings (`MCPARR_*` env vars)
- **Package Manager:** uv
- **Linting:** Ruff (configured in pyproject.toml)
- **Type Checking:** Pyright
- **Testing:** pytest + pytest-asyncio
- **Issues:** Beads (`bd`)

## Commands

```bash
make dev        # Start development server
make check      # Lint + typecheck
make fix        # Auto-fix lint issues
make test       # Run tests
make docker-build  # Build Docker image
```

## Project Structure

```
src/mcparr/
  __main__.py       # Entry point
  server.py         # FastMCP server, health endpoint, system status tool
  config.py         # Pydantic Settings (MCPARR_* env vars)
  clients/
    base.py         # BaseArrClient — shared auth, HTTP methods
    sonarr.py       # Sonarr v3 API
    radarr.py       # Radarr v3 API
    prowlarr.py     # Prowlarr v1 API
    sabnzbd.py      # SABnzbd CGI-style API
    bazarr.py       # Bazarr REST API
  tools/
    sonarr.py       # TV show tools (5)
    radarr.py       # Movie tools (5)
    sabnzbd.py      # Download tools (4)
    prowlarr.py     # Indexer tools (2)
    bazarr.py       # Subtitle tools (2)
```

## Architecture

- Tools register conditionally — only services with valid URL + API key get tools
- Each service module has a `register(mcp)` function called from `server.py`
- Clients are initialized in the lifespan context and shared across tool invocations
- SABnzbd has its own client (CGI-style API), all others inherit from `BaseArrClient`
- Deployed behind agentgateway — tools appear as `arr_*` in Claude

## Beads

This project uses **bd** (beads) for issue tracking.

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

1. **File issues for remaining work** — Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) — Tests, linters, builds
3. **Update issue status** — Close finished work, update in-progress items
4. **PUSH TO REMOTE** — This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** — Clear stashes, prune remote branches
6. **Verify** — All changes committed AND pushed
7. **Hand off** — Provide context for next session
