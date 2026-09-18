"""Process configuration loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Process configuration read from `JSF_`-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="JSF_", env_file=".env", extra="ignore")

    app_name: str = "job-status-found"
    """Service name shown in OpenAPI."""

    version: str = "0.1.0"
    """Build version shown in OpenAPI."""

    cors_allow_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    """Browser origins allowed to call the API; defaults to any local development port."""


@lru_cache
def get_settings() -> AppSettings:
    """Return the process-wide settings, reading the environment on first call.

    Returns:
        The cached `AppSettings` instance.
    """
    return AppSettings()
