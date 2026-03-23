# Contributing

## Getting Started

1. Fork and clone the repository
2. Install dependencies: `uv sync`
3. Copy `.env.example` to `.env` and fill in API keys
4. Run the dev server: `make dev`

## Development Setup

- **Python 3.12+** required
- **uv** for package management
- **Ruff** for linting and formatting
- **Pyright** for type checking

## Code Style

- Run `make check` before committing
- Run `make fix` to auto-fix lint/format issues
- All code MUST have type annotations
- Use `from __future__ import annotations` in every module

## Commit Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(sonarr): add episode search tool
fix(sabnzbd): handle empty queue response
docs: update configuration reference
```

## Pull Requests

- Create a feature branch from `main`
- Keep PRs focused — one feature or fix per PR
- Include tests for new functionality
- Ensure `make check` passes
- Use closing keywords: "Closes #123" or "Fixes #123"
