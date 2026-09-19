"""Argon2id password hashing through `pwdlib`."""

import anyio.to_thread
from anyio import CapacityLimiter
from pwdlib import PasswordHash

_PASSWORD_HASH = PasswordHash.recommended()
"""`pwdlib`'s recommended Argon2id hasher, which uses 64 MiB per hash."""


async def hash_password(password: str, *, limiter: CapacityLimiter) -> str:
    """Hash a password in a worker thread once the limiter admits it.

    One hash holds 64 MiB for tens of milliseconds, so it runs off the event
    loop, and the limiter caps how many run at once to keep the process's memory
    bounded.

    Args:
        password: The password in the clear.
        limiter: Caps the hashes that run at the same time across all requests.

    Returns:
        The Argon2id PHC string, including its salt and parameters.
    """
    return await anyio.to_thread.run_sync(_PASSWORD_HASH.hash, password, limiter=limiter)
