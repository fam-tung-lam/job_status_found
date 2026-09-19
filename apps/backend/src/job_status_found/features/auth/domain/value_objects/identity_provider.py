"""External identity providers supported by the auth feature."""

from enum import StrEnum


class IdentityProvider(StrEnum):
    """An external system that can prove an account identity."""

    GOOGLE = "google"
    """Google OpenID Connect."""
