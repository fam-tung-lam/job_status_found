"""An open emailed challenge as auth operations see it."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class EmailChallenge:
    """One open emailed code that may still be answered."""

    id: UUID
    """The challenge's surrogate key."""

    owner_id: UUID
    """The account that must answer the challenge."""

    secret_hash: bytes
    """The keyed hash of the emailed code."""

    attempt_count: int
    """Wrong answers made against this challenge."""

    expires_at: datetime
    """The instant at which the challenge stops working."""

    consumed_at: datetime | None
    """When the challenge was answered or exhausted."""
