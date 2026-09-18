import pytest

from job_status_found.app.app_settings import AppSettings


def test_database_settings_come_from_prefixed_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the environment Compose gives the backend container.
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
