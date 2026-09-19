"""An emailed code or link about to be stored."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)


@dataclass(frozen=True, slots=True)
class NewEmailChallengeDTO:
    """A challenge that replaces the user's open challenge of the same purpose."""

    owner_id: UUID
    """The user who must answer."""

    purpose: EmailChallengePurpose
    """What answering proves."""

    secret_hash: bytes
    """HMAC-SHA-256 of the code or link token; the secret itself is never stored."""

    created_at: datetime
    """When the challenge is sent."""

    expires_at: datetime
    """When the code or link stops working."""
