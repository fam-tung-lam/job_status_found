"""Verification codes hashed with HMAC-SHA-256 and the server key."""

import hashlib
import hmac


def hash_verification_code(code: str, *, hmac_key: bytes) -> bytes:
    """Hash a verification code for storage and comparison.

    A 6-digit code has too little entropy for a bare hash: anyone holding the
    table could try all million values. The server key makes the stored value
    reveal nothing without it. The same code always gives the same hash, so a
    submitted code is checked by hashing it and comparing.

    Args:
        code: The verification code in the clear.
        hmac_key: The secret HMAC key from the auth settings.

    Returns:
        The 32-byte digest to store in `email_challenges.secret_hash`.
    """
    return hmac.digest(hmac_key, code.encode(), hashlib.sha256)
