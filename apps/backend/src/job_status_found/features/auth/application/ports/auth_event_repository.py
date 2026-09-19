"""Storage of security events."""

from datetime import datetime
from typing import Protocol
from uuid import UUID


class AuthEventRepository(Protocol):
    """Records security events inside the caller's transaction."""

    async def record(self, owner_id: UUID, event_type: str, occurred_at: datetime) -> None:
        """Record that a security event happened to a user.

        Args:
            owner_id: The user the event concerns.
            event_type: What happened, such as `existing_account_notice_sent`.
            occurred_at: When it happened.
        """
        ...

    async def find_latest_created_at(self, owner_id: UUID, event_type: str) -> datetime | None:
        """Find when an event of a type last happened to a user.

        Args:
            owner_id: The user the events concern.
            event_type: The event type to look at.

        Returns:
            The newest `created_at`, or `None` when no such event exists.
        """
        ...
