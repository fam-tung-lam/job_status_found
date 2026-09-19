"""Unit tests of loading `AuthSettings` from the environment."""

import json

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

    @pytest.mark.parametrize(
        ("cookie_secure", "cookie_name"),
        [("true", "jsf_refresh"), ("false", "__Secure-jsf_refresh")],
    )
    def test_cookie_security_and_its_required_name_prefix_cannot_disagree(
        self,
        monkeypatch: pytest.MonkeyPatch,
        cookie_secure: str,
        cookie_name: str,
    ) -> None:
        """
        Given: cookie security and the reserved `__Secure-` prefix disagree.
        When: auth settings are loaded.
        Then: start-up rejects the cookie configuration.
        """
        # Given: otherwise-valid auth secrets and a mismatched cookie name.
        key = "unit-test-auth-key-with-at-least-32-characters"
        monkeypatch.setenv("JSF_AUTH_HMAC_KEY", key)
        monkeypatch.setenv("JSF_AUTH_JWT_SIGNING_KEY_ID", "test")
        monkeypatch.setenv("JSF_AUTH_JWT_KEY_RING", json.dumps({"test": key}))
        monkeypatch.setenv("JSF_AUTH_COOKIE_SECURE", cookie_secure)
        monkeypatch.setenv("JSF_AUTH_REFRESH_COOKIE_NAME", cookie_name)

        # When: auth settings are loaded.
        # Then: start-up rejects the cookie configuration.
        with pytest.raises(ValidationError, match="refresh cookie"):
            AuthSettings(_env_file=None)
