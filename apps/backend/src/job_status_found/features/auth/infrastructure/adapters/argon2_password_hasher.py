"""Argon2id password hashing through `pwdlib`."""

import anyio.to_thread
from anyio import CapacityLimiter
from pwdlib import PasswordHash


class Argon2PasswordHasher:
    """`PasswordHasher` with Argon2id at 64 MiB, run in worker threads.

    One hash holds 64 MiB for tens of milliseconds, so it runs off the event
    loop, and the limiter caps how many run at once to keep the process's memory
    bounded.
    """

    def __init__(self, limiter: CapacityLimiter) -> None:
        """Hash with `pwdlib`'s recommended Argon2id parameters.

        Args:
            limiter: Caps the hashes that run at the same time across all requests.
        """
        self._password_hash = PasswordHash.recommended()
        self._limiter = limiter

    async def hash(self, password: str) -> str:
        """Hash a password in a worker thread once the limiter admits it.

        Args:
            password: The password in the clear.

        Returns:
            The Argon2id PHC string, including its salt and parameters.
        """
        return await anyio.to_thread.run_sync(
            self._password_hash.hash, password, limiter=self._limiter
        )
