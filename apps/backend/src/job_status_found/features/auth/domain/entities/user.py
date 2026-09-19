"""An account as the auth operations see it."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    """One account, identified by its id and reached at its email address."""

    id: UUID
    """The account's surrogate key."""

    email: str
    """The address mail is delivered to, as the user typed it."""

    email_verified_at: datetime | None
    """When the user proved control of the mailbox; `None` while unverified."""

    @property
    def is_email_verified(self) -> bool:
        """Whether someone has proven control of the account's mailbox."""
        return self.email_verified_at is not None
