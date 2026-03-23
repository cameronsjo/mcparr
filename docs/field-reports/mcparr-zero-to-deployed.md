# mcparr: Zero to Deployed MCP Server — Field Report

**Date:** 2026-03-23
**Type:** architecture
**Project:** cameronsjo/mcparr

## Goal

Replace the broken third-party `mcp-servarr` (from bdfrost) with a custom-built MCP server that covers the full *arr media automation stack — Sonarr, Radarr, Prowlarr, SABnzbd, Bazarr — deployed behind agentgateway on an Unraid homelab. The old server only supported Radarr and Sonarr, and the codebase was effectively non-functional.

The target: go from empty directory to a working, deployed, release-pipelined MCP server in a single session.

## Architecture

### Language Choice: Python + FastMCP

Evaluated Python, Rust, and TypeScript. Python won on pragmatic grounds:

| Factor | Python | Rust | TypeScript |
|--------|--------|------|------------|
| MCP SDK maturity | FastMCP 3.1 — battle-tested | rmcp — young | Official SDK — mature |
| Dev velocity | 19 tools in one session | Unlikely in one session | Possible but verbose |
| Performance bottleneck | Network I/O (irrelevant) | Network I/O (irrelevant) | Network I/O (irrelevant) |
| Existing convention | media-mcp is TypeScript | None in stack | media-mcp |

The existing `media-mcp` is TypeScript, so matching language was considered. But this server is an API proxy — 99% of execution time is waiting on HTTP round-trips to *arr services. Python's conciseness for wrapping REST APIs outweighed language consistency. FastMCP's decorator-based tool registration is significantly less ceremony than the TypeScript SDK's class-based approach for this use case.

### Client Architecture: BaseArrClient + Thin Subclasses

Sonarr, Radarr, Prowlarr, and Bazarr all descend from the same codebase and share API patterns: `X-Api-Key` header auth, `/api/v{n}/` path prefix, JSON request/response. A shared `BaseArrClient` handles auth, request building, and error normalization. Each service subclass only adds its domain-specific methods.

SABnzbd is the exception — it uses a CGI-style `?mode=&apikey=` API that has nothing in common with the *arr pattern. It gets its own standalone client.

**Why not pyarr?** Considered using pyarr (Python wrapper for *arr APIs, 77.5 benchmark score). Decided against it — the APIs are simple enough that a thin httpx client gives us full control without an abstraction layer. When you're already behind an MCP tool layer, adding another wrapper is indirection that hurts debugging without adding value.

### Conditional Tool Registration

The most interesting design decision. Instead of registering all 19 tools and returning errors when a service isn't configured:

```python
if settings.sonarr.enabled:
    from servarr.tools.sonarr import register as register_sonarr
    register_sonarr(mcp)
```

Services with empty `URL` or `API_KEY` simply don't register their tools. The LLM's tool list is always truthful — every tool it sees will work. This also saves tokens on tool descriptions for unconfigured services.

### Agentgateway Target Naming

Named the agentgateway target `arr` instead of `mcparr` or `servarr`. Since agentgateway prepends the target name to all tools (`prefixMode: always`), this means tools appear as `arr_search_movies`, `arr_get_downloads`, `arr_pause_downloads`. Short, instantly recognizable, no redundancy.

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python | Network I/O bottleneck makes Rust/TS advantages irrelevant |
| HTTP client | httpx (not pyarr) | Thinner dependency, full control, simpler debugging |
| Transport | Streamable HTTP | Required for agentgateway; SSE is deprecated in MCP spec |
| Tool design | Action-oriented | `search_movies` not `radarr_get_movie_endpoint` |
| Tool registration | Conditional | Unconfigured services don't pollute the tool list |
| Env prefix | `MCPARR_` | Per-service nested: `MCPARR_SONARR_URL`, `MCPARR_RADARR_API_KEY` |
| Health endpoint | `/health` alongside `/mcp` | FastMCP's `@custom_route` makes this trivial |
| Container name | `mcparr` | Renamed from `mcp-servarr` to match the new project |

## Pipeline Overview

The build strategy used parallel agents to maximize throughput:

```
Phase 1: Foundation (sequential — everything depends on this)
  ├── git init, uv init, dependencies
  ├── config.py (Pydantic Settings)
  ├── server.py (FastMCP, lifespan, health endpoint)
  └── clients/base.py (BaseArrClient)

Phase 2: Service implementations (5 agents in parallel)
  ├── Agent 1: Sonarr client + 5 tools
  ├── Agent 2: Radarr client + 5 tools
  ├── Agent 3: SABnzbd client + 4 tools
  ├── Agent 4: Prowlarr client + 2 tools
  └── Agent 5: Bazarr client + 2 tools

Phase 3: Packaging (sequential)
  ├── Dockerfile (multi-stage, non-root, OCI labels)
  ├── GitHub repo creation
  ├── CI/CD workflows (lint, publish, release-please)
  └── Homelab integration (compose, agentgateway, SOPS secrets)
```

All 5 service agents ran simultaneously. Each received a detailed prompt with the exact API endpoints, authentication patterns, tool annotations, and code conventions. They wrote both the client and tools files independently. Total parallel agent time: ~2 minutes for all 5 services.

## What Worked

**Parallel agent strategy paid off.** The 5 service implementations are truly independent — different API endpoints, different tool signatures, no shared state beyond the base class. Running them in parallel cut what would have been 15-20 minutes of sequential work into ~2 minutes wall clock.

**FastMCP's decorator API is excellent for this use case.** Tool registration is concise:

```python
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def search_movies(ctx: Context, query: str) -> list[dict[str, Any]]:
```

Compare to the TypeScript SDK's class-based approach — easily 3x more ceremony for the same result.

**Pydantic Settings with nested configs** handled the multi-service configuration cleanly. Each service gets its own env prefix (`MCPARR_SONARR_*`) via a separate `ServiceConfig` subclass with its own `SettingsConfigDict`.

**GHCR publish with SLSA attestation** was straightforward — `docker/build-push-action` + `actions/attest-build-provenance` in 50 lines of YAML.

## What Didn't Work

**Skipped a-star-is-born scaffold.** The plan explicitly called for it in Step 1, but I scaffolded manually "because I knew what was needed." This violated plan execution discipline and left the project missing AGENTS.md, LICENSE, CONTRIBUTING, SECURITY, Beads, release-please, and docs/adr. Had to retrofit it later.

**Dockerfile missed README.md.** The `pyproject.toml` references `readme = "README.md"` and uv_build tries to read it during `uv sync`. The first CI build failed because README.md wasn't in the Docker COPY layer. Fixed by adding it to the COPY command.

**uv_build version constraint was too tight.** `uv_build>=0.10.2,<0.11.0` failed in CI where uv 0.11.0 was installed. Relaxed to `>=0.10.2`.

**Rename mid-session created churn.** Renaming from `servarr` to `mcparr` after the initial commit touched every file. If we'd settled the name before coding, it would have been one commit instead of two. The directory on disk is still `~/Projects/servarr/` which is a minor ongoing annoyance.

## Gotchas

- **Bazarr API key wasn't in SOPS.** All other *arr API keys were there, but bazarr was missing. Had to SSH to Unraid and grab it from `/mnt/user/appdata/bazarr/config/config.yaml`.
- **agentgateway target was missing from config.** The old `mcp-servarr` target had been removed from the active agentgateway config at some point — it wasn't in either listener's target list. Had to add `arr` to both external (8080) and internal (8081) listeners.
- **FastMCP's internal tool storage API is not public.** Tried `mcp._tool_manager._tools`, `mcp._tools`, `mcp.get_tools()` before finding `await mcp.list_tools()`. The public async API works; the internal attributes don't.
- **Old container needs manual cleanup.** Bosun deploys the new `mcparr` container but doesn't remove the orphaned `mcp-servarr`. Requires `docker rm -f mcp-servarr` manually.

## Key Takeaways

- **Parallel agents work best when the units are truly independent.** The 5 service modules share a base class but have zero runtime coupling — perfect for parallelization. If there had been cross-service tools (e.g., "get unified queue"), the agents would have needed coordination.
- **Conditional tool registration is the right pattern for multi-service MCP servers.** Don't show tools that can't work. The LLM's context is precious — every dead tool wastes tokens and creates confusion.
- **Name things before you build them.** The servarr → mcparr rename was unnecessary friction. Settle the name during planning, not after the first commit.
- **Follow the plan.** Skipping a-star-is-born didn't save time — it created a retrofit task later. The plan exists to prevent exactly this kind of "I'll do it faster my way" drift.
- **API proxies don't need fast languages.** When your server spends 99% of its time waiting on network I/O, the language runtime is irrelevant. Choose for developer velocity and ecosystem maturity.
