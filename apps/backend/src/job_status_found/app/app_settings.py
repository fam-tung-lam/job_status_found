"""Process configuration loaded from the environment."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

_DATABASE_CONNECT_TIMEOUT_SECONDS = 5


class AppSettings(BaseSettings):
    """Process configuration read from `JSF_`-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="JSF_", env_file=".env", extra="ignore")

    app_name: str = "job-status-found"
    """Service name shown in OpenAPI."""

    version: str = "0.1.0"
    """Build version shown in OpenAPI."""

    cors_allow_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    """Browser origins allowed to call the API; defaults to any local development port."""

    database_host: str = "localhost"
    """PostgreSQL server host name."""

    database_port: int = 5432
    """PostgreSQL server TCP port."""

    database_name: str = "job_status_found"
    """PostgreSQL database name."""

    database_user: str = "job_status_found"
    """PostgreSQL role the service connects as."""

    database_password: SecretStr | None = None
    """Password for `database_user`; `None` sends no password."""

    @property
    def database_url(self) -> URL:
        """The URL of the configured PostgreSQL database for the psycopg driver.

        The async application engine and the synchronous Alembic run share it,
        because psycopg 3 provides both. The password stays verbatim and is
        hidden when the URL is printed. A connection attempt gives up after
        `_DATABASE_CONNECT_TIMEOUT_SECONDS`, instead of psycopg's default of
        130 seconds.
        """
        password = self.database_password
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.database_user,
            password=password.get_secret_value() if password is not None else None,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
            query={"connect_timeout": str(_DATABASE_CONNECT_TIMEOUT_SECONDS)},
        )


@lru_cache
def get_settings() -> AppSettings:
    """Return the process-wide settings, reading the environment on first call.

    Returns:
        The cached `AppSettings` instance.
    """
    return AppSettings()
