"""Storage of security events."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_auth_event_dto import NewAuthEventDTO
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType


class AuthEventRepository(Protocol):
    """Records security events inside the caller's transaction."""

    async def record_auth_event(
        self, owner_id: UUID, event_type: AuthEventType, occurred_at: datetime
    ) -> None:
        """Record that a security event happened to a user.

        Args:
            owner_id: The user the event concerns.
            event_type: What happened, such as `existing_account_notice_sent`.
            occurred_at: When it happened.
        """
        ...

    async def find_last_auth_event_occurred_at(
        self, owner_id: UUID, event_type: AuthEventType
    ) -> datetime | None:
        """Find when an event of a type last happened to a user.

        Args:
            owner_id: The user the events concern.
            event_type: The event type to look at.

        Returns:
            The newest `created_at`, or `None` when no such event exists.
        """
        ...

    async def create_auth_event(self, auth_event: NewAuthEventDTO) -> None:
        """Store a security event.

        Args:
            auth_event: The non-secret facts to store.
        """
        ...

    async def count_auth_events_since(
        self, owner_id: UUID, event_type: AuthEventType, occurred_since: datetime
    ) -> int:
        """Count an owner's events of a type in a time window.

        Args:
            owner_id: The account the events concern.
            event_type: The event type to count.
            occurred_since: The inclusive start of the window.

        Returns:
            The number of matching events.
        """
        ...
