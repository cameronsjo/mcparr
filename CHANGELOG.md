# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-23

### Added

- Initial release with 19 MCP tools across 5 services
- Sonarr tools: search_series, get_series, add_series, get_series_queue, get_series_calendar
- Radarr tools: search_movies, get_movie, add_movie, get_movie_queue, get_movie_calendar
- SABnzbd tools: get_downloads, get_download_history, pause_downloads, resume_downloads
- Prowlarr tools: search_indexers, get_indexer_stats
- Bazarr tools: get_wanted_subtitles, search_subtitles
- System tool: get_system_status
- Streamable HTTP transport on configurable host/port/path
- Graceful service degradation (unconfigured services don't register tools)
- Docker image published to GHCR with SLSA attestation
