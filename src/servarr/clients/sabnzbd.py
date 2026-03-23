"""SABnzbd API client. Uses CGI-style ?mode= parameters, not REST."""

from __future__ import annotations

from typing import Any

import httpx


class SabnzbdError(Exception):
    """Raised when a SABnzbd API call fails."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"SABnzbd API error ({status_code}): {message}")


class SabnzbdClient:
    """SABnzbd API client. Uses CGI-style ?mode= parameters."""

    service_name = "sabnzbd"

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _call(self, mode: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a SABnzbd API call.

        Builds URL: {base_url}/api?mode={mode}&apikey={apikey}&output=json&{extra}
        """
        query: dict[str, Any] = {
            "mode": mode,
            "apikey": self.api_key,
            "output": "json",
        }
        if params:
            query.update(params)

        response = await self._client.get("/api", params=query)
        if not response.is_success:
            raise SabnzbdError(response.status_code, response.text[:500])
        return response.json()

    async def get_queue(self) -> dict[str, Any]:
        """Get current download queue with speed, remaining size, and jobs."""
        data = await self._call("queue")
        return data.get("queue", data)

    async def get_history(self, limit: int = 20) -> dict[str, Any]:
        """Get download history."""
        data = await self._call("history", {"limit": limit})
        return data.get("history", data)

    async def pause(self, minutes: int | None = None) -> dict[str, Any]:
        """Pause the download queue.

        Without minutes: pauses indefinitely.
        With minutes: pauses for the specified duration then auto-resumes.
        """
        if minutes is not None:
            return await self._call("config", {"name": "set_pause", "value": minutes})
        return await self._call("pause")

    async def resume(self) -> dict[str, Any]:
        """Resume the download queue."""
        return await self._call("resume")

    async def system_status(self) -> dict[str, Any]:
        """Get combined system status: version, speed, and queue state."""
        version_data = await self._call("version")
        queue_data = await self.get_queue()
        return {
            "version": version_data.get("version", "unknown"),
            "speed": queue_data.get("speed", "0"),
            "speed_limit": queue_data.get("speedlimit", ""),
            "paused": queue_data.get("paused", False),
            "status": queue_data.get("status", "unknown"),
            "disk_space_1": queue_data.get("diskspace1", ""),
            "disk_space_2": queue_data.get("diskspace2", ""),
            "total_remaining": queue_data.get("sizeleft", "0 B"),
            "eta": queue_data.get("timeleft", "0:00:00"),
            "active_jobs": len(queue_data.get("slots", [])),
        }

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
