# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.2](https://github.com/cameronsjo/mcparr/compare/v0.1.1...v0.1.2) (2026-03-23)


### Documentation

* add field report — zero to deployed MCP server ([9114637](https://github.com/cameronsjo/mcparr/commit/91146373b6fa3223f03110004a2ce02844b2ca0a))

## [0.1.1](https://github.com/cameronsjo/mcparr/compare/v0.1.0...v0.1.1) (2026-03-23)


### Features

* apply essentials scaffold ([2977932](https://github.com/cameronsjo/mcparr/commit/2977932711072da81b5192f607264219f6e5ab3e))
* initial servarr MCP server ([99c490a](https://github.com/cameronsjo/mcparr/commit/99c490a0c8329620ce6d43f4afd1ca6a67db3262))


### Bug Fixes

* include README.md in Docker build, relax uv_build constraint ([ff970f7](https://github.com/cameronsjo/mcparr/commit/ff970f7d327e0d93f71001f8d8979b3957237afd))


### Documentation

* add README with usage, config, and tool reference ([76c3540](https://github.com/cameronsjo/mcparr/commit/76c3540940d3fc6ed77351ab64879f641c617420))

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
