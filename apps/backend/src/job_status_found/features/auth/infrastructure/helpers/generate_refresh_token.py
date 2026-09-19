"""Refresh tokens from the operating system's secure random source."""

import secrets

_REFRESH_TOKEN_BYTE_COUNT = 32
"""Random bytes in a refresh token, giving 256 bits of entropy."""


def generate_refresh_token() -> str:
    """Create a URL-safe opaque refresh token.

    Returns:
        A token with 256 random bits before base64url encoding.
    """
    return secrets.token_urlsafe(_REFRESH_TOKEN_BYTE_COUNT)
