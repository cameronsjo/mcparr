"""API clients for *arr services."""

from servarr.clients.base import ArrClientError, BaseArrClient
from servarr.clients.bazarr import BazarrClient
from servarr.clients.prowlarr import ProwlarrClient
from servarr.clients.radarr import RadarrClient
from servarr.clients.sabnzbd import SabnzbdClient
from servarr.clients.sonarr import SonarrClient

__all__ = [
    "ArrClientError",
    "BaseArrClient",
    "BazarrClient",
    "ProwlarrClient",
    "RadarrClient",
    "SabnzbdClient",
    "SonarrClient",
]
