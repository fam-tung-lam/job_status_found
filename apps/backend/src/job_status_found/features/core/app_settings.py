"""Process-wide configuration loaded from the environment."""

from functools import lru_cache
from typing import Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings
from sqlalchemy import URL

from job_status_found.features.core.infrastructure.clients.smtp_email_sender_client import (
    SmtpSecurity,
)
from job_status_found.features.core.infrastructure.settings_config import settings_config

_DATABASE_CONNECT_TIMEOUT_SECONDS = 5
"""Seconds a database connection attempt waits, instead of psycopg's default of 130."""


class AppSettings(BaseSettings):
    """Process configuration read from `JSF_`-prefixed environment variables.

    It holds what the whole application shares: the service, the database, and
    the clients every feature uses, such as the SMTP server. A migration run
    loads it too, so every value it needs has a default or comes from `.env`.
    A feature's own values, such as the auth feature's, live in that feature's
    settings class.
    """

    model_config = settings_config("JSF_")

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

    smtp_host: str = "localhost"
    """Host name of the SMTP server that delivers every feature's email."""

    smtp_port: int = 587
    """TCP port of the SMTP server."""

    smtp_security: SmtpSecurity = "starttls"
    """How the SMTP connection is protected.

    `starttls` upgrades a plain connection and fails when the server cannot,
    `tls` connects with implicit TLS, usually on port 465, and `none` sends in
    the clear, which only a local development server such as Mailpit should
    accept.
    """

    smtp_username: str | None = None
    """SMTP user name; `None` skips authentication."""

    smtp_password: SecretStr | None = None
    """Password for `smtp_username`."""

    smtp_sender: str = "JSV <no-reply@localhost>"
    """`From` address of every email; production sets its verified sending domain."""

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

    @model_validator(mode="after")
    def _refuse_smtp_credentials_in_the_clear(self) -> Self:
        """Stop the start-up when SMTP credentials would travel unencrypted.

        Returns:
            The settings, unchanged, when `smtp_security` protects the credentials
            or none are set.

        Raises:
            ValueError: `smtp_security` is `none` and a user name or password is set.
        """
        if self.smtp_security == "none" and (
            self.smtp_username is not None or self.smtp_password is not None
        ):
            msg = "smtp_security `none` would send the SMTP credentials in the clear."
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> AppSettings:
    """Return the process-wide settings, reading the environment on first call.

    Returns:
        The cached `AppSettings` instance.
    """
    return AppSettings()
