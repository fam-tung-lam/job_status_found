"""Normalized sign-in identifiers hashed with HMAC-SHA-256."""

import hashlib
import hmac


def hash_auth_identifier(identifier: str, *, hmac_key: bytes) -> bytes:
    """Hash a normalized identifier for audit and throttling without storing it.

    Args:
        identifier: The normalized email address.
        hmac_key: The auth feature's server-side HMAC key.

    Returns:
        The 32-byte keyed digest.
    """
    return hmac.digest(hmac_key, b"auth-identifier:\x00" + identifier.encode(), hashlib.sha256)
