"""Password hashing."""

from typing import Protocol


class PasswordHasher(Protocol):
    """Turns a password into a slow, salted hash."""

    async def hash(self, password: str) -> str:
        """Hash a password without blocking the event loop.

        Args:
            password: The password in the clear.

        Returns:
            A self-describing hash string that includes its algorithm and parameters.
        """
        ...
