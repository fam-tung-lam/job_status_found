import pytest
from pydantic import ValidationError

from job_status_found.features.auth.auth_settings import AuthSettings


def test_a_rejected_secret_setting_stays_out_of_the_startup_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: an HMAC key shorter than the 32 characters the settings require.
    monkeypatch.setenv("JSF_AUTH_TERMS_VERSION", "2026-09-18")
    monkeypatch.setenv("JSF_AUTH_HMAC_KEY", "too-short-but-still-secret")

    # When: the auth settings are loaded.
    with pytest.raises(ValidationError) as rejection:
        AuthSettings(_env_file=None)

    # Then: the error names the setting but never repeats its value.
    assert "hmac_key" in str(rejection.value)
    assert "too-short-but-still-secret" not in str(rejection.value)
