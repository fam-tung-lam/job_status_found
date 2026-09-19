"""Storage of emailed codes and links."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_email_challenge import (
    NewEmailChallenge,
)
from job_status_found.features.auth.domain.entities.email_challenge import EmailChallenge
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)


class EmailChallengeRepository(Protocol):
    """Reads and writes email challenges inside the caller's transaction."""

    async def find_last_email_challenge_sent_at(
        self, owner_id: UUID, purpose: EmailChallengePurpose
    ) -> datetime | None:
        """Find when the user was last sent a challenge of a purpose.

        Consumed challenges count, because they were sent; replaced ones are gone.

        Args:
            owner_id: The user the challenges were sent to.
            purpose: The purpose to look at.

        Returns:
            The newest `created_at`, or `None` when no such challenge exists.
        """
        ...

    async def replace_open_email_challenge(self, challenge: NewEmailChallenge) -> None:
        """Store a challenge and delete the user's open one of the same purpose.

        Afterwards only the new challenge's code or link works.

        Args:
            challenge: The challenge to store.
        """
        ...

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
        ...

    async def register_wrong_email_challenge_answer(
        self, challenge_id: UUID, *, attempt_count: int, consumed_at: datetime | None
    ) -> None:
        """Store a wrong answer count and consume the challenge when exhausted.

        Args:
            challenge_id: The challenge answered incorrectly.
            attempt_count: The new wrong-answer count.
            consumed_at: When exhausted, or `None` while attempts remain.
        """
        ...

    async def consume_email_challenge(self, challenge_id: UUID, consumed_at: datetime) -> None:
        """Mark a successfully answered challenge as consumed.

        Args:
            challenge_id: The answered challenge.
            consumed_at: When it was answered.
        """
        ...
