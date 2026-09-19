"""Sessions and refresh-token families in PostgreSQL."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO
from job_status_found.features.auth.domain.entities.session_with_refresh_token import (
    RefreshTokenChild,
    SessionWithRefreshToken,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.session_revocation_reason import (
    SessionRevocationReason,
)
from job_status_found.features.auth.domain.value_objects.sign_in_method import SignInMethod
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.auth.infrastructure.db.tables import (
    RefreshTokenTable,
    SessionTable,
    UserTable,
)


class SqlSessionRepository:
    """`SessionRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request session; the use case commits it.
        """
        self._session = session

    async def create_session(
        self,
        owner_id: UUID,
        session_input: SessionInputDTO,
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
        row = SessionTable()
        row.user_id = owner_id
        row.sign_in_method = SignInMethod.PASSWORD.value
        row.client_kind = session_input.client_kind.value
        row.is_persistent = session_input.remember_me
        row.ip_address = session_input.ip_address
        row.user_agent = session_input.user_agent
        row.created_at = created_at
        row.authenticated_at = created_at
        row.last_refreshed_at = created_at
        row.idle_expires_at = idle_expires_at
        row.absolute_expires_at = absolute_expires_at
        row.revoked_at = None
        row.revocation_reason = None
        self._session.add(row)
        await self._session.flush()
        return row.id

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
        row = RefreshTokenTable()
        row.session_id = session_id
        row.parent_token_id = parent_token_id
        row.token_hash = token_hash
        row.created_at = created_at
        row.expires_at = expires_at
        row.used_at = None
        row.revoked_at = None
        self._session.add(row)
        await self._session.flush()
        return row.id

    async def lock_session_by_refresh_token_hash(
        self, token_hash: bytes
    ) -> SessionWithRefreshToken | None:
        """Find a refresh token and lock its session until the transaction ends.

        Args:
            token_hash: SHA-256 of the presented token.

        Returns:
            The token and locked session, or `None` when the token is unknown.
        """
        statement = (
            select(SessionTable, RefreshTokenTable, UserTable)
            .join(RefreshTokenTable, RefreshTokenTable.session_id == SessionTable.id)
            .join(UserTable, UserTable.id == SessionTable.user_id)
            .where(RefreshTokenTable.token_hash == token_hash)
            # Lock both rows. Locking only the session can leave the joined
            # token columns from the statement's earlier snapshot stale after
            # a concurrent rotation releases the session lock.
            .with_for_update(of=(SessionTable, RefreshTokenTable))
        )
        row = (await self._session.execute(statement)).one_or_none()
        if row is None:
            return None
        session, token, user = row
        return SessionWithRefreshToken(
            session_id=session.id,
            owner_id=session.user_id,
            role=UserRole(user.role),
            client_kind=ClientKind(session.client_kind),
            is_persistent=session.is_persistent,
            is_user_suspended=user.suspended_at is not None,
            is_user_pending_deletion=user.deletion_requested_at is not None,
            idle_expires_at=session.idle_expires_at,
            absolute_expires_at=session.absolute_expires_at,
            session_revoked_at=session.revoked_at,
            token_id=token.id,
            token_expires_at=token.expires_at,
            token_used_at=token.used_at,
            token_revoked_at=token.revoked_at,
        )

    async def find_refresh_token_child(self, parent_token_id: UUID) -> RefreshTokenChild | None:
        """Find the newest direct child of a spent token.

        Args:
            parent_token_id: The spent parent token.

        Returns:
            Its direct child, or `None` when none exists.
        """
        row = await self._session.scalar(
            select(RefreshTokenTable)
            .where(RefreshTokenTable.parent_token_id == parent_token_id)
            .order_by(RefreshTokenTable.created_at.desc())
            .limit(1)
        )
        if row is None:
            return None
        return RefreshTokenChild(
            id=row.id,
            is_used=row.used_at is not None,
            is_revoked=row.revoked_at is not None,
        )

    async def mark_refresh_token_used(self, token_id: UUID, used_at: datetime) -> None:
        """Mark a refresh token as exchanged.

        Args:
            token_id: The token that was exchanged.
            used_at: When the exchange happened.
        """
        await self._session.execute(
            update(RefreshTokenTable)
            .where(RefreshTokenTable.id == token_id)
            .values({RefreshTokenTable.used_at: used_at})
        )

    async def revoke_refresh_token(self, token_id: UUID, revoked_at: datetime) -> None:
        """Revoke one refresh token.

        Args:
            token_id: The token to revoke.
            revoked_at: When it was revoked.
        """
        await self._session.execute(
            update(RefreshTokenTable)
            .where(RefreshTokenTable.id == token_id)
            .values({RefreshTokenTable.revoked_at: revoked_at})
        )

    async def refresh_session(
        self, session_id: UUID, *, refreshed_at: datetime, idle_expires_at: datetime
    ) -> None:
        """Move a session's last refresh and sliding idle expiry.

        Args:
            session_id: The session to refresh.
            refreshed_at: When the refresh succeeded.
            idle_expires_at: The clamped new idle expiry.
        """
        await self._session.execute(
            update(SessionTable)
            .where(SessionTable.id == session_id)
            .values(
                {
                    SessionTable.last_refreshed_at: refreshed_at,
                    SessionTable.idle_expires_at: idle_expires_at,
                }
            )
        )

    async def lock_session_by_id(self, owner_id: UUID, session_id: UUID) -> bool:
        """Lock an owner's session for bearer-token sign-out.

        Args:
            owner_id: The account that must own the session.
            session_id: The session asserted by the access token.

        Returns:
            Whether the session exists and belongs to the owner.
        """
        locked_id = await self._session.scalar(
            select(SessionTable.id)
            .where(SessionTable.id == session_id, SessionTable.user_id == owner_id)
            .with_for_update()
        )
        return locked_id is not None

    async def revoke_session_and_refresh_tokens(
        self,
        session_id: UUID,
        *,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> None:
        """Revoke a session and every token in its family together.

        Args:
            session_id: The session to end.
            revoked_at: When it ended.
            reason: The stored revocation reason.
        """
        await self._session.execute(
            update(SessionTable)
            .where(SessionTable.id == session_id, SessionTable.revoked_at.is_(None))
            .values(
                {
                    SessionTable.revoked_at: revoked_at,
                    SessionTable.revocation_reason: reason.value,
                }
            )
        )
        await self._session.execute(
            update(RefreshTokenTable)
            .where(
                RefreshTokenTable.session_id == session_id,
                RefreshTokenTable.revoked_at.is_(None),
            )
            .values({RefreshTokenTable.revoked_at: revoked_at})
        )
