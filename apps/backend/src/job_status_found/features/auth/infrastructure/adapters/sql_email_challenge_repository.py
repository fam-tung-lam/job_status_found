"""Emailed codes and links in the PostgreSQL `email_challenges` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.new_email_challenge_dto import (
    NewEmailChallengeDTO,
)
from job_status_found.features.auth.domain.entities.email_challenge import EmailChallenge
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

    async def replace_open_email_challenge(self, challenge: NewEmailChallengeDTO) -> None:
        """Store a challenge and delete the user's open one of the same purpose.

        Args:
            challenge: The challenge to store.
        """
        # Delete the open challenge first; the partial unique index allows only
        # one open challenge per user and purpose.
        await self._session.execute(
            delete(EmailChallengeTable).where(
                EmailChallengeTable.user_id == challenge.owner_id,
                EmailChallengeTable.purpose == challenge.purpose,
                EmailChallengeTable.consumed_at.is_(None),
            )
        )

        # Store the new challenge, unanswered.
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

    async def lock_open_email_challenge(
        self, owner_id: UUID, purpose: EmailChallengePurpose
    ) -> EmailChallenge | None:
        """Find and lock an owner's open challenge of a purpose.

        Args:
            owner_id: The user who must answer.
            purpose: What answering proves.

        Returns:
            The locked open challenge, or `None` when none exists.
        """
        row = await self._session.scalar(
            select(EmailChallengeTable)
            .where(
                EmailChallengeTable.user_id == owner_id,
                EmailChallengeTable.purpose == purpose,
                EmailChallengeTable.consumed_at.is_(None),
            )
            .with_for_update()
        )
        if row is None:
            return None
        return EmailChallenge(
            id=row.id,
            owner_id=row.user_id,
            secret_hash=row.secret_hash,
            attempt_count=row.attempt_count,
            expires_at=row.expires_at,
            consumed_at=row.consumed_at,
        )

    async def register_wrong_email_challenge_answer(
        self, challenge_id: UUID, *, attempt_count: int, consumed_at: datetime | None
    ) -> None:
        """Store a wrong answer count and consume the challenge when exhausted.

        Args:
            challenge_id: The challenge answered incorrectly.
            attempt_count: The new wrong-answer count.
            consumed_at: When exhausted, or `None` while attempts remain.
        """
        await self._session.execute(
            update(EmailChallengeTable)
            .where(EmailChallengeTable.id == challenge_id)
            .values(
                {
                    EmailChallengeTable.attempt_count: attempt_count,
                    EmailChallengeTable.consumed_at: consumed_at,
                }
            )
        )

    async def consume_email_challenge(self, challenge_id: UUID, consumed_at: datetime) -> None:
        """Mark a successfully answered challenge as consumed.

        Args:
            challenge_id: The answered challenge.
            consumed_at: When it was answered.
        """
        await self._session.execute(
            update(EmailChallengeTable)
            .where(EmailChallengeTable.id == challenge_id)
            .values({EmailChallengeTable.consumed_at: consumed_at})
        )
