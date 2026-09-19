"""The identity established by one access token."""

from dataclasses import dataclass
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """The account, session, and role asserted by a verified access token."""

    user_id: UUID
    """The authenticated account."""

    session_id: UUID
    """The session that issued the access token."""

    role: UserRole
    """The role asserted when the token was issued."""
