# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/
RUN uv sync --frozen --no-dev

# Stage 2: Production
FROM python:3.12-slim AS production

LABEL org.opencontainers.image.source="https://github.com/cameronsjo/servarr" \
      org.opencontainers.image.description="Unified MCP server for the *arr media automation stack" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Non-root user
RUN groupadd -g 1001 servarr && useradd -u 1001 -g servarr -m servarr

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

USER servarr

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SERVARR_HOST=0.0.0.0 \
    SERVARR_PORT=8080 \
    SERVARR_PATH=/mcp \
    SERVARR_LOG_LEVEL=info

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health').read()"

CMD ["python", "-m", "servarr"]
