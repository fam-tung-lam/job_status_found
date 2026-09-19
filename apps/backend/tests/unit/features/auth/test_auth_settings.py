"""Unit tests of loading `AuthSettings` from the environment."""

import pytest
from pydantic import ValidationError

from job_status_found.features.auth.auth_settings import AuthSettings


class TestAuthSettings:
    """Loading `AuthSettings` from `JSF_AUTH_*` environment variables."""

    def test_a_rejected_secret_setting_stays_out_of_the_startup_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Given: an HMAC key shorter than the settings require.
        When: the auth settings are loaded.
        Then: the validation error names the setting but not its value.
        """
        # Given: an HMAC key shorter than the 32 characters the settings require.
        monkeypatch.setenv("JSF_AUTH_HMAC_KEY", "too-short-but-still-secret")

        # When: the auth settings are loaded.
        with pytest.raises(ValidationError) as rejection:
            AuthSettings(_env_file=None)

        # Then: the error names the setting but never repeats its value.
        assert "hmac_key" in str(rejection.value)
        assert "too-short-but-still-secret" not in str(rejection.value)
