"""A locked session and one token from its refresh family."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class SessionWithRefreshToken:
    """The state needed to decide one refresh while its session row is locked."""

    session_id: UUID
    """The locked session."""

    owner_id: UUID
    """The account that owns the session."""

    role: UserRole
    """The account's current role for the next access token."""

    client_kind: ClientKind
    """The channel fixed when the session was created."""

    is_persistent: bool
    """Whether the session survives a browser restart."""

    is_user_suspended: bool
    """Whether the account is currently suspended."""

    is_user_pending_deletion: bool
    """Whether the account is waiting to be deleted."""

    idle_expires_at: datetime
    """When inactivity ends the session."""

    absolute_expires_at: datetime
    """When the session ends regardless of activity."""

    session_revoked_at: datetime | None
    """When the session ended explicitly."""

    token_id: UUID
    """The presented refresh-token row."""

    token_expires_at: datetime
    """When the presented token stops working."""

    token_used_at: datetime | None
    """When the presented token was first rotated."""

    token_revoked_at: datetime | None
    """When the presented token was revoked."""


@dataclass(frozen=True, slots=True)
class RefreshTokenChild:
    """The current direct child of a spent refresh token."""

    id: UUID
    """The child token's row id."""

    is_used: bool
    """Whether the child has itself been rotated."""

    is_revoked: bool
    """Whether the child has been revoked."""
