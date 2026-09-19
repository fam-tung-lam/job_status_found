"""Argon2id password verification and opportunistic rehashing through `pwdlib`."""

import anyio.to_thread
from anyio import CapacityLimiter
from pwdlib import PasswordHash

_ARGON2ID_PASSWORD_HASHER = PasswordHash.recommended()
"""The same recommended Argon2id configuration used for new password hashes."""


async def verify_and_update_password(
    password: str, password_hash: str, *, limiter: CapacityLimiter
) -> tuple[bool, str | None]:
    """Verify a password and return a stronger replacement hash when needed.

    Args:
        password: The submitted password in the clear.
        password_hash: The stored PHC string, real or dummy.
        limiter: Caps concurrent memory-intensive Argon2id work.

    Returns:
        Whether the password matched and a replacement hash when the stored
        parameters are older than the recommended ones.
    """
    return await anyio.to_thread.run_sync(
        _ARGON2ID_PASSWORD_HASHER.verify_and_update,
        password,
        password_hash,
        limiter=limiter,
    )
