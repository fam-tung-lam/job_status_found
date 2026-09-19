"""Storage of password hashes."""

from datetime import datetime
from typing import Protocol
from uuid import UUID


class PasswordCredentialRepository(Protocol):
    """Reads and writes password hashes inside the caller's transaction."""

    async def set_password_hash(
        self, owner_id: UUID, password_hash: str, changed_at: datetime
    ) -> None:
        """Set a user's password hash, adding the credential when the user has none.

        Args:
            owner_id: The user whose password this is.
            password_hash: The Argon2id PHC string; never the password itself.
            changed_at: When the password was set.
        """
        ...

    async def find_password_hash(self, owner_id: UUID) -> str | None:
        """Find the password hash of an account.

        Args:
            owner_id: The account whose password is requested.

        Returns:
            The Argon2id PHC string, or `None` for a social-only account.
        """
        ...
