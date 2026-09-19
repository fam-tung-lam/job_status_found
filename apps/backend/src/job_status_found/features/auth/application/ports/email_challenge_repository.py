"""Storage of emailed codes and links."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_email_challenge import (
    NewEmailChallenge,
)
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
