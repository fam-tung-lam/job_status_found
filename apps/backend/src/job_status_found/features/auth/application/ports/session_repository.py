"""Storage of sessions and their rotating refresh-token families."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.session_input import SessionInput
from job_status_found.features.auth.domain.entities.session_with_refresh_token import (
    RefreshTokenChild,
    SessionWithRefreshToken,
)
from job_status_found.features.auth.domain.value_objects.session_revocation_reason import (
    SessionRevocationReason,
)


class SessionRepository(Protocol):
    """Reads and changes sessions inside the caller's transaction."""

    async def create_session(
        self,
        owner_id: UUID,
        session_input: SessionInput,
        *,
        created_at: datetime,
        idle_expires_at: datetime,
        absolute_expires_at: datetime,
    ) -> UUID:
        """Create a password session and return its generated id.

        Args:
            owner_id: The account opening the session.
            session_input: The client and request facts to store.
            created_at: The instant of credential proof and session creation.
            idle_expires_at: When inactivity ends the session.
            absolute_expires_at: The session's fixed final expiry.

        Returns:
            The generated session id.
        """
        ...

    async def create_refresh_token(
        self,
        session_id: UUID,
        token_hash: bytes,
        *,
        parent_token_id: UUID | None,
        created_at: datetime,
        expires_at: datetime,
    ) -> UUID:
        """Store one refresh token and return its generated id.

        Args:
            session_id: The token family's session.
            token_hash: SHA-256 of the opaque token.
            parent_token_id: The spent token this one replaces, if any.
            created_at: When the token was issued.
            expires_at: When the token stops working.

        Returns:
            The generated token-row id.
        """
        ...

    async def lock_session_by_refresh_token_hash(
        self, token_hash: bytes
    ) -> SessionWithRefreshToken | None:
        """Find a refresh token and lock its session until the transaction ends.

        Args:
            token_hash: SHA-256 of the presented token.

        Returns:
            The token and locked session, or `None` when the token is unknown.
        """
        ...

    async def find_refresh_token_child(self, parent_token_id: UUID) -> RefreshTokenChild | None:
        """Find the newest direct child of a spent token.

        Args:
            parent_token_id: The spent parent token.

        Returns:
            Its direct child, or `None` when none exists.
        """
        ...

    async def mark_refresh_token_used(self, token_id: UUID, used_at: datetime) -> None:
        """Mark a refresh token as exchanged.

        Args:
            token_id: The token that was exchanged.
            used_at: When the exchange happened.
        """
        ...

    async def revoke_refresh_token(self, token_id: UUID, revoked_at: datetime) -> None:
        """Revoke one refresh token.

        Args:
            token_id: The token to revoke.
            revoked_at: When it was revoked.
        """
        ...

    async def refresh_session(
        self, session_id: UUID, *, refreshed_at: datetime, idle_expires_at: datetime
    ) -> None:
        """Move a session's last refresh and sliding idle expiry.

        Args:
            session_id: The session to refresh.
            refreshed_at: When the refresh succeeded.
            idle_expires_at: The clamped new idle expiry.
        """
        ...

    async def lock_session_by_id(self, owner_id: UUID, session_id: UUID) -> bool:
        """Lock an owner's session for bearer-token sign-out.

        Args:
            owner_id: The account that must own the session.
            session_id: The session asserted by the access token.

        Returns:
            Whether the session exists and belongs to the owner.
        """
        ...

    async def revoke_session_and_refresh_tokens(
        self, session_id: UUID, *, revoked_at: datetime, reason: SessionRevocationReason
    ) -> None:
        """Revoke a session and every token in its family together.

        Args:
            session_id: The session to end.
            revoked_at: When it ended.
            reason: The stored revocation reason.
        """
        ...
