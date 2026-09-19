"""OAuth token types returned by the auth API."""

from enum import StrEnum


class AuthTokenType(StrEnum):
    """How a client sends an access token."""

    BEARER = "Bearer"
    """An access token sent through the HTTP Authorization header."""
