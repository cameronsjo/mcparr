# mcparr

Unified MCP server for the \*arr media automation stack.

Provides 19 action-oriented tools across 5 services for managing media acquisition, downloads, and subtitles via the [Model Context Protocol](https://modelcontextprotocol.io).

## Services

| Service | Tools | What it does |
|---------|------:|--------------|
| **Sonarr** | 5 | TV series — search, add, queue, calendar |
| **Radarr** | 5 | Movies — search, add, queue, calendar |
| **SABnzbd** | 4 | Downloads — queue, history, pause/resume |
| **Prowlarr** | 2 | Indexers — search, stats |
| **Bazarr** | 2 | Subtitles — wanted, search |
| **System** | 1 | Health and version info across all services |

Services with missing configuration are gracefully disabled — only configured tools appear in the tool list.

## Quick Start

```bash
# Clone and install
git clone https://github.com/cameronsjo/mcparr.git
cd mcparr
uv sync

# Configure (copy and fill in API keys)
cp .env.example .env

# Run
uv run python -m mcparr
```

The server starts on `http://0.0.0.0:8080/mcp` (Streamable HTTP transport).

## Configuration

All configuration via environment variables with `MCPARR_` prefix:

```bash
# Server
MCPARR_HOST=0.0.0.0
MCPARR_PORT=8080
MCPARR_PATH=/mcp
MCPARR_LOG_LEVEL=info

# Services (empty URL = disabled)
MCPARR_SONARR_URL=http://sonarr:8989
MCPARR_SONARR_API_KEY=your-api-key

MCPARR_RADARR_URL=http://radarr:7878
MCPARR_RADARR_API_KEY=your-api-key

MCPARR_PROWLARR_URL=http://prowlarr:9696
MCPARR_PROWLARR_API_KEY=your-api-key

MCPARR_SABNZBD_URL=http://sabnzbd:8080
MCPARR_SABNZBD_API_KEY=your-api-key

MCPARR_BAZARR_URL=http://bazarr:6767
MCPARR_BAZARR_API_KEY=your-api-key
```

## Docker

```bash
# Build
docker build -t mcparr .

# Run
docker run --env-file .env -p 8080:8080 mcparr
```

Pre-built image: `ghcr.io/cameronsjo/mcparr:latest`

## Tools

### Movies (Radarr)

- **search_movies** — Search library or look up new movies by title
- **get_movie** — Get details for a specific movie by ID
- **add_movie** — Add a movie to Radarr for monitoring and download
- **get_movie_queue** — Get movie download queue with progress
- **get_movie_calendar** — Get upcoming movie releases

### TV Shows (Sonarr)

- **search_series** — Search library or look up new TV series by title
- **get_series** — Get details for a specific series with season breakdown
- **add_series** — Add a series to Sonarr for monitoring and download
- **get_series_queue** — Get TV episode download queue with progress
- **get_series_calendar** — Get upcoming episode air dates

### Downloads (SABnzbd)

- **get_downloads** — Current download queue with speed, progress, ETA
- **get_download_history** — Completed download history
- **pause_downloads** — Pause download queue (optionally for N minutes)
- **resume_downloads** — Resume download queue

### Indexers (Prowlarr)

- **search_indexers** — Search across all configured indexers
- **get_indexer_stats** — Indexer performance statistics

### Subtitles (Bazarr)

- **get_wanted_subtitles** — Movies and episodes missing subtitles
- **search_subtitles** — Trigger subtitle search for a movie or episode

### System

- **get_system_status** — Health and version info for all configured services

## Development

```bash
make check    # Lint + typecheck
make fix      # Auto-fix lint issues
make test     # Run tests
make dev      # Start dev server
```

## License

MIT
