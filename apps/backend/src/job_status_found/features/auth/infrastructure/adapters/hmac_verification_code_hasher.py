"""Verification codes hashed with HMAC-SHA-256 and the server key."""

import hashlib
import hmac


class HmacVerificationCodeHasher:
    """`VerificationCodeHasher` on Python's `hmac` module."""

    def __init__(self, hmac_key: bytes) -> None:
        """Hash codes with one server key.

        Args:
            hmac_key: The secret HMAC key from the auth settings.
        """
        self._hmac_key = hmac_key

    def hash_verification_code(self, code: str) -> bytes:
        """Hash a verification code with HMAC-SHA-256 and the server key.

        Args:
            code: The verification code in the clear.

        Returns:
            The 32-byte digest.
        """
        return hmac.digest(self._hmac_key, code.encode(), hashlib.sha256)
