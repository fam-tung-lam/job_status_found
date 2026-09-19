"""An account as the auth operations see it."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class User:
    """One account, identified by its id and reached at its email address."""

    id: UUID
    """The account's surrogate key."""

    email: str
    """The address mail is delivered to, as the user typed it."""

    email_verified_at: datetime | None
    """When the user proved control of the mailbox; `None` while unverified."""

    first_name: str | None = None
    """The account's given name, when known."""

    last_name: str | None = None
    """The account's family name, when known."""

    avatar_url: str | None = None
    """The account's provider picture URL, when one exists."""

    locale: str | None = None
    """The account's preferred BCP 47 locale, when known."""

    role: UserRole = UserRole.USER
    """The account's current instance-level role."""

    suspended_at: datetime | None = None
    """When the account was suspended; `None` while active."""

    deletion_requested_at: datetime | None = None
    """When deletion was requested; `None` while the account is available."""

    @property
    def is_email_verified(self) -> bool:
        """Whether someone has proven control of the account's mailbox."""
        return self.email_verified_at is not None

    @property
    def is_available(self) -> bool:
        """Whether the account may open or refresh a session."""
        return self.suspended_at is None and self.deletion_requested_at is None
