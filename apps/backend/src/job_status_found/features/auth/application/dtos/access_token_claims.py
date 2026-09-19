"""Claims needed to issue one access token."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    """The authenticated facts and issue time of an access token."""

    owner_id: UUID
    """The account represented by `sub`."""

    session_id: UUID
    """The session represented by `sid`."""

    role: UserRole
    """The account role at issue time."""

    issued_at: datetime
    """The token's issue time."""
