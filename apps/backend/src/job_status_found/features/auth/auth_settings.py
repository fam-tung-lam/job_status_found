"""Configuration of the auth feature, loaded from the environment."""

from datetime import timedelta
from functools import lru_cache
from typing import Annotated, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings

from job_status_found.features.core import settings_config


class AuthSettings(BaseSettings):
    """Auth configuration read from `JSF_AUTH_`-prefixed environment variables.

    Only the serving application needs it, so a migration runs without the
    auth secrets. `di.py` hands its values to adapters, use cases, and
    controllers.
    """

    model_config = settings_config("JSF_AUTH_")

    hmac_key: Annotated[SecretStr, Field(min_length=32)]
    """Server key for HMAC-SHA-256 of emailed codes; at least 32 characters, never logged."""

    password_min_length: Annotated[int, Field(ge=8, le=128)] = 12
    """Fewest Unicode code points a new password may have; the maximum is always 128."""

    verification_code_lifetime: timedelta = timedelta(minutes=15)
    """How long an emailed verification code stays valid."""

    verification_code_send_interval: timedelta = timedelta(seconds=60)
    """Shortest time between two sign-up emails, a code or a notice, to the same user."""

    sign_up_min_response_time: timedelta = timedelta(milliseconds=500)
    """Shortest time an accepted sign-up takes to answer.

    Every branch then answers at the same moment, so its few milliseconds of
    work never reveal whether the email has an account. Keep it above the
    slowest sign-up, whose Argon2id hash dominates.
    """

    jwt_issuer: str = "http://localhost:8000"
    """Exact `iss` claim of first-party access tokens."""

    jwt_audience: str = "job-status-found-api"
    """Exact `aud` claim of first-party access tokens."""

    jwt_signing_key_id: str
    """Key-ring entry used to sign new access tokens."""

    jwt_key_ring: dict[str, SecretStr]
    """HS256 keys by `kid`, including the signing key and verify-only old keys."""

    access_token_lifetime: timedelta = timedelta(minutes=15)
    """How long a bearer access token works."""

    persistent_session_idle_lifetime: timedelta = timedelta(days=30)
    """Sliding idle lifetime when `remember_me` is true."""

    persistent_session_absolute_lifetime: timedelta = timedelta(days=180)
    """Fixed session lifetime when `remember_me` is true."""

    non_persistent_session_idle_lifetime: timedelta = timedelta(hours=24)
    """Sliding idle lifetime when `remember_me` is false."""

    non_persistent_session_absolute_lifetime: timedelta = timedelta(days=7)
    """Fixed session lifetime when `remember_me` is false."""

    refresh_reuse_grace: timedelta = timedelta(seconds=10)
    """How soon a lost refresh response may safely be retried."""

    refresh_cookie_name: str = "__Secure-jsf_refresh"
    """Name of the web-only HTTP-only refresh cookie."""

    cookie_secure: bool = True
    """Whether the refresh cookie requires HTTPS."""

    @model_validator(mode="after")
    def _validate_token_settings(self) -> Self:
        """Reject missing, short, or internally inconsistent token settings.

        Returns:
            The validated settings.

        Raises:
            ValueError: The signing key is absent, a key is too short, or a
                secure cookie lacks the required prefix.
        """
        if self.jwt_signing_key_id not in self.jwt_key_ring:
            error_message = "jwt_signing_key_id must name a key in jwt_key_ring."
            raise ValueError(error_message)
        if any(len(key.get_secret_value()) < 32 for key in self.jwt_key_ring.values()):
            error_message = "Every JWT key must contain at least 32 characters."
            raise ValueError(error_message)
        if self.cookie_secure and not self.refresh_cookie_name.startswith("__Secure-"):
            error_message = "A secure refresh cookie name must start with `__Secure-`."
            raise ValueError(error_message)
        if not self.cookie_secure and self.refresh_cookie_name.startswith("__Secure-"):
            error_message = "An insecure local refresh cookie cannot use the `__Secure-` prefix."
            raise ValueError(error_message)
        return self


@lru_cache
def get_auth_settings() -> AuthSettings:
    """Return the process-wide auth settings, reading the environment on first call.

    Returns:
        The cached `AuthSettings` instance.
    """
    return AuthSettings()
