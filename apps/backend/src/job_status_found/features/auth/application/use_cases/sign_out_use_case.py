"""End a session by refresh credential or authenticated principal."""

from collections.abc import Callable
from datetime import datetime

from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.value_objects.session_revocation_reason import (
    SessionRevocationReason,
)
from job_status_found.features.core import UnitOfWork


class SignOutUseCase:
    """Revoke the addressed session and its refresh-token family idempotently."""

    def __init__(
        self,
        *,
        sessions: SessionRepository,
        unit_of_work: UnitOfWork,
        hash_refresh_token: Callable[[str], bytes],
        utc_now: Callable[[], datetime],
    ) -> None:
        """Keep storage, hashing, and time collaborators.

        Args:
            sessions: Locks and revokes sessions.
            unit_of_work: Commits the idempotent result.
            hash_refresh_token: Hashes an optional refresh credential for lookup.
            utc_now: Tells the revocation instant.
        """
        self._sessions = sessions
        self._unit_of_work = unit_of_work
        self._hash_refresh_token = hash_refresh_token
        self._utc_now = utc_now

    async def invoke(
        self,
        *,
        refresh_token: str | None,
        principal: AuthenticatedPrincipal | None,
    ) -> None:
        """End the session addressed by the preferred available credential.

        Args:
            refresh_token: The cookie or body credential, preferred when present.
            principal: The bearer principal used only without a refresh token.
        """
        now = self._utc_now()
        session_id = None
        if refresh_token is not None:
            state = await self._sessions.lock_session_by_refresh_token_hash(
                self._hash_refresh_token(refresh_token)
            )
            if state is not None:
                session_id = state.session_id
        if (
            session_id is None
            and principal is not None
            and await self._sessions.lock_session_by_id(principal.user_id, principal.session_id)
        ):
            session_id = principal.session_id

        if session_id is not None:
            await self._sessions.revoke_session_and_refresh_tokens(
                session_id,
                revoked_at=now,
                reason=SessionRevocationReason.SIGNED_OUT,
            )
        await self._unit_of_work.commit()
