"""Security events in the PostgreSQL `auth_events` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        self, owner_id: UUID, event_type: str, occurred_at: datetime
    ) -> None:
        """Record that a security event happened to a user.

        Args:
            owner_id: The user the event concerns.
            event_type: What happened, such as `existing_account_notice_sent`.
            occurred_at: When it happened.
        """
        row = AuthEventTable()
        row.user_id = owner_id
        row.event_type = event_type
        row.identifier_hash = None
        row.ip_address = None
        row.user_agent = None
        row.details = None
        row.created_at = occurred_at
        self._session.add(row)

    async def find_last_auth_event_occurred_at(
        self, owner_id: UUID, event_type: str
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
                AuthEventTable.user_id == owner_id, AuthEventTable.event_type == event_type
            )
        )
