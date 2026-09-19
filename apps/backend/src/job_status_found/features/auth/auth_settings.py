"""Configuration of the auth feature, loaded from the environment."""

from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr
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


@lru_cache
def get_auth_settings() -> AuthSettings:
    """Return the process-wide auth settings, reading the environment on first call.

    Returns:
        The cached `AuthSettings` instance.
    """
    return AuthSettings()
