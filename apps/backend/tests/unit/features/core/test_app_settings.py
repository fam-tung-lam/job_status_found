"""Unit tests of loading `AppSettings` from the environment."""

import pytest
from pydantic import ValidationError

from job_status_found.features.core import AppSettings


def test_database_settings_come_from_prefixed_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the environment Compose gives the backend container, which a
    # migration run also uses, with no auth values.
    monkeypatch.setenv("JSF_DATABASE_HOST", "postgres")
    monkeypatch.setenv("JSF_DATABASE_NAME", "jobs")
    monkeypatch.setenv("JSF_DATABASE_USER", "jobs_user")
    monkeypatch.setenv("JSF_DATABASE_PASSWORD", "p@ss:word/with?reserved#chars")

    # When: the settings are loaded without a `.env` file.
    settings = AppSettings(_env_file=None)

    # Then: the database fields hold the container values, and the password is
    # read verbatim and masked when printed.
    assert settings.database_host == "postgres"
    assert settings.database_name == "jobs"
    assert settings.database_user == "jobs_user"
    assert settings.database_password is not None
    assert settings.database_password.get_secret_value() == "p@ss:word/with?reserved#chars"
    assert "p@ss" not in repr(settings)


def test_an_empty_optional_setting_means_its_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: optional SMTP credentials that Compose passes as empty strings.
    monkeypatch.setenv("JSF_SMTP_USERNAME", "")
    monkeypatch.setenv("JSF_SMTP_PASSWORD", "")

    # When: the settings are loaded.
    settings = AppSettings(_env_file=None)

    # Then: no credentials are configured, so no SMTP login is attempted.
    assert settings.smtp_username is None
    assert settings.smtp_password is None


def test_smtp_credentials_on_an_unprotected_connection_are_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: SMTP credentials with a connection that sends them in the clear.
    monkeypatch.setenv("JSF_SMTP_SECURITY", "none")
    monkeypatch.setenv("JSF_SMTP_USERNAME", "resend")
    monkeypatch.setenv("JSF_SMTP_PASSWORD", "re_secret")

    # When: the settings are loaded.
    # Then: start-up stops instead of leaking the credentials.
    with pytest.raises(ValidationError, match="in the clear"):
        AppSettings(_env_file=None)
