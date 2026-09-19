"""Keyed hashing of the 6-digit codes emailed to verify a mailbox."""

from typing import Protocol


class VerificationCodeHasher(Protocol):
    """Hashes verification codes with a server key, for storage and comparison.

    A 6-digit code has too little entropy for a bare hash: anyone holding the
    table could try all million values. The server key makes the stored value
    reveal nothing without it.
    """

    def hash_verification_code(self, code: str) -> bytes:
        """Hash a verification code with HMAC-SHA-256 and the server key.

        The same code always gives the same hash, so a submitted code is
        checked by hashing it and comparing.

        Args:
            code: The verification code in the clear.

        Returns:
            The 32-byte digest to store in `email_challenges.secret_hash`.
        """
        ...
