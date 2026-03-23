"""API clients for *arr services."""

from mcparr.clients.base import ArrClientError, BaseArrClient
from mcparr.clients.bazarr import BazarrClient
from mcparr.clients.prowlarr import ProwlarrClient
from mcparr.clients.radarr import RadarrClient
from mcparr.clients.sabnzbd import SabnzbdClient
from mcparr.clients.sonarr import SonarrClient

__all__ = [
    "ArrClientError",
    "BaseArrClient",
    "BazarrClient",
    "ProwlarrClient",
    "RadarrClient",
    "SabnzbdClient",
    "SonarrClient",
]
