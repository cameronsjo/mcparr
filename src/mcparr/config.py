"""Configuration via environment variables with MCPARR_ prefix."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    """Config for a single *arr service. Empty url means disabled."""

    url: str = ""
    api_key: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.api_key)


class SonarrConfig(ServiceConfig):
    model_config = SettingsConfigDict(env_prefix="MCPARR_SONARR_")


class RadarrConfig(ServiceConfig):
    model_config = SettingsConfigDict(env_prefix="MCPARR_RADARR_")


class ProwlarrConfig(ServiceConfig):
    model_config = SettingsConfigDict(env_prefix="MCPARR_PROWLARR_")


class SabnzbdConfig(ServiceConfig):
    model_config = SettingsConfigDict(env_prefix="MCPARR_SABNZBD_")


class BazarrConfig(ServiceConfig):
    model_config = SettingsConfigDict(env_prefix="MCPARR_BAZARR_")


class Settings(BaseSettings):
    """Top-level server settings."""

    model_config = SettingsConfigDict(env_prefix="MCPARR_")

    # Transport
    host: str = "0.0.0.0"
    port: int = 8080
    path: str = "/mcp"
    log_level: str = Field(default="info", pattern=r"^(debug|info|warning|error)$")

    # Service configs (loaded from individual env prefixes)
    sonarr: SonarrConfig = Field(default_factory=SonarrConfig)
    radarr: RadarrConfig = Field(default_factory=RadarrConfig)
    prowlarr: ProwlarrConfig = Field(default_factory=ProwlarrConfig)
    sabnzbd: SabnzbdConfig = Field(default_factory=SabnzbdConfig)
    bazarr: BazarrConfig = Field(default_factory=BazarrConfig)

    @property
    def enabled_services(self) -> list[str]:
        return [
            name
            for name in ("sonarr", "radarr", "prowlarr", "sabnzbd", "bazarr")
            if getattr(self, name).enabled
        ]
