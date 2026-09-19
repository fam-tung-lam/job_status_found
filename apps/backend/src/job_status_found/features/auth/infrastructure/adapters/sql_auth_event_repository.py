"""Security events in the PostgreSQL `auth_events` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.new_auth_event import NewAuthEvent
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.auth.infrastructure.db.tables import AuthEventTable


class SqlAuthEventRepository:
    """`AuthEventRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request's database session; the use case commits it.
        """
        self._session = session

    async def record_auth_event(
        self, owner_id: UUID, event_type: AuthEventType, occurred_at: datetime
    ) -> None:
        """Record that a security event happened to a user.

        Args:
            owner_id: The user the event concerns.
            event_type: What happened, such as `existing_account_notice_sent`.
            occurred_at: When it happened.
        """
        row = AuthEventTable()
        row.user_id = owner_id
        row.event_type = event_type.value
        row.identifier_hash = None
        row.ip_address = None
        row.user_agent = None
        row.details = None
        row.created_at = occurred_at
        self._session.add(row)

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
        return await self._session.scalar(
            select(func.max(AuthEventTable.created_at)).where(
                AuthEventTable.user_id == owner_id,
                AuthEventTable.event_type == event_type.value,
            )
        )

    async def create_auth_event(self, auth_event: NewAuthEvent) -> None:
        """Store a security event.

        Args:
            auth_event: The non-secret facts to store.
        """
        row = AuthEventTable()
        row.user_id = auth_event.owner_id
        row.event_type = auth_event.event_type.value
        row.identifier_hash = auth_event.identifier_hash
        row.ip_address = auth_event.ip_address
        row.user_agent = auth_event.user_agent
        row.details = auth_event.details
        row.created_at = auth_event.occurred_at
        self._session.add(row)

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
        count = await self._session.scalar(
            select(func.count())
            .select_from(AuthEventTable)
            .where(
                AuthEventTable.user_id == owner_id,
                AuthEventTable.event_type == event_type.value,
                AuthEventTable.created_at >= occurred_since,
            )
        )
        return int(count or 0)
