"""Base client for *arr APIs that use X-Api-Key auth and /api/v{n}/ paths."""

from __future__ import annotations

from typing import Any

import httpx


class ArrClientError(Exception):
    """Raised when an *arr API call fails."""

    def __init__(self, service: str, status_code: int, message: str) -> None:
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API error ({status_code}): {message}")


class BaseArrClient:
    """Shared base for Sonarr, Radarr, Prowlarr, and Bazarr API clients.

    Handles auth, request building, and error normalization.
    """

    service_name: str = "arr"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_version: str = "v3",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_prefix = f"/api/{api_version}" if api_version else "/api"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Api-Key": api_key},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    def _url(self, path: str) -> str:
        """Build full API path."""
        return f"{self.api_prefix}/{path.lstrip('/')}"

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._client.request(
            method,
            self._url(path),
            params=params,
            json=json,
        )
        if not response.is_success:
            body = response.text[:500]
            raise ArrClientError(self.service_name, response.status_code, body)
        if response.status_code == 204:
            return None
        return response.json()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", path, json=json)

    async def put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> Any:
        return await self._request("DELETE", path)

    async def system_status(self) -> dict[str, Any]:
        """Get system status — common across all *arr services."""
        return await self.get("system/status")
