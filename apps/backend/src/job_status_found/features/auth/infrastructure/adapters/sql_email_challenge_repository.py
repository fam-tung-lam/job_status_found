"""Emailed codes and links in the PostgreSQL `email_challenges` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.new_email_challenge import (
    NewEmailChallenge,
)
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.auth.infrastructure.db.tables import EmailChallengeTable


class SqlEmailChallengeRepository:
    """`EmailChallengeRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request's database session; the use case commits it.
        """
        self._session = session

    async def find_last_email_challenge_sent_at(
        self, owner_id: UUID, purpose: EmailChallengePurpose
    ) -> datetime | None:
        """Find when the user was last sent a challenge of a purpose.

        Args:
            owner_id: The user the challenges were sent to.
            purpose: The purpose to look at.

        Returns:
            The newest `created_at`, or `None` when no such challenge exists.
        """
        return await self._session.scalar(
            select(func.max(EmailChallengeTable.created_at)).where(
                EmailChallengeTable.user_id == owner_id,
                EmailChallengeTable.purpose == purpose,
            )
        )

    async def replace_open_email_challenge(self, challenge: NewEmailChallenge) -> None:
        """Store a challenge and delete the user's open one of the same purpose.

        Args:
            challenge: The challenge to store.
        """
        await self._session.execute(
            delete(EmailChallengeTable).where(
                EmailChallengeTable.user_id == challenge.owner_id,
                EmailChallengeTable.purpose == challenge.purpose,
                EmailChallengeTable.consumed_at.is_(None),
            )
        )
        row = EmailChallengeTable()
        row.user_id = challenge.owner_id
        row.purpose = challenge.purpose
        row.secret_hash = challenge.secret_hash
        row.new_email = None
        row.attempt_count = 0
        row.created_at = challenge.created_at
        row.expires_at = challenge.expires_at
        row.consumed_at = None
        self._session.add(row)
