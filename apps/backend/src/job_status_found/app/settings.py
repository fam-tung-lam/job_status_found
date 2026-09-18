"""Process configuration loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Process configuration read from `JSF_`-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="JSF_", env_file=".env", extra="ignore")

    app_name: str = "job-status-found"
    """Service name shown in OpenAPI."""

    version: str = "0.1.0"
    """Build version shown in OpenAPI."""


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, reading the environment on first call.

    Returns:
        The cached `Settings` instance.
    """
    return Settings()
