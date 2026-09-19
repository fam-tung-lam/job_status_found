"""Refresh tokens hashed with SHA-256 for storage and lookup."""

import hashlib


def hash_refresh_token(refresh_token: str) -> bytes:
    """Hash a high-entropy refresh token for storage.

    Args:
        refresh_token: The opaque credential in the clear.

    Returns:
        Its 32-byte SHA-256 digest.
    """
    return hashlib.sha256(refresh_token.encode()).digest()
