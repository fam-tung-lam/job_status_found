"""Rotate refresh tokens, tolerate one lost response, and detect replay."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from job_status_found.features.auth.application.dtos.new_auth_event_dto import NewAuthEventDTO
from job_status_found.features.auth.application.dtos.token_pair_dto import TokenPairDTO
from job_status_found.features.auth.application.ports.auth_event_repository import (
    AuthEventRepository,
)
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.application.use_cases.issue_rotated_tokens_use_case import (
    IssueRotatedTokensUseCase,
)
from job_status_found.features.auth.domain.failures.session_refresh_failure import (
    SessionRefreshOriginNotAllowedFailure,
    SessionRefreshSessionEndedFailure,
    SessionRefreshTokenInvalidFailure,
)
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.session_revocation_reason import (
    SessionRevocationReason,
)
from job_status_found.features.core import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SessionRefreshSettings:
    """The sliding session lifetimes and lost-response grace."""

    persistent_idle_lifetime: timedelta
    """The sliding idle lifetime of a persistent session."""

    non_persistent_idle_lifetime: timedelta
    """The sliding idle lifetime of a non-persistent session."""

    reuse_grace: timedelta
    """How soon one retry may replace an unused child."""

    def idle_lifetime_for(self, *, is_persistent: bool) -> timedelta:
        """Return the idle lifetime selected by persistence.

        Args:
            is_persistent: Whether the session remembers the device.

        Returns:
            The configured sliding lifetime.
        """
        if is_persistent:
            return self.persistent_idle_lifetime
        return self.non_persistent_idle_lifetime


class RefreshSessionUseCase:
    """Rotate one refresh family under its session-row lock."""

    def __init__(
        self,
        *,
        sessions: SessionRepository,
        auth_events: AuthEventRepository,
        issue_rotated_tokens: IssueRotatedTokensUseCase,
        unit_of_work: UnitOfWork,
        hash_refresh_token: Callable[[str], bytes],
        utc_now: Callable[[], datetime],
        settings: SessionRefreshSettings,
    ) -> None:
        """Keep the session store, audit store, helpers, and rules.

        Args:
            sessions: Locks and changes the refresh family.
            auth_events: Records detected replay.
            issue_rotated_tokens: Issues the next access and refresh tokens.
            unit_of_work: Commits each outcome once.
            hash_refresh_token: Hashes the presented opaque credential.
            utc_now: Tells the current instant.
            settings: The sliding lifetimes and retry grace.
        """
        self._sessions = sessions
        self._auth_events = auth_events
        self._issue_rotated_tokens = issue_rotated_tokens
        self._unit_of_work = unit_of_work
        self._hash_refresh_token = hash_refresh_token
        self._utc_now = utc_now
        self._settings = settings

    async def invoke(self, refresh_token: str, *, is_origin_allowed: bool) -> TokenPairDTO:
        """Rotate a refresh token and return committed replacement credentials.

        Args:
            refresh_token: The opaque token from the fixed client channel.
            is_origin_allowed: Whether the browser Origin matches the CORS allow-list.

        Returns:
            The replacement token pair.

        Raises:
            SessionRefreshTokenInvalidFailure: No token row matches the credential.
            SessionRefreshSessionEndedFailure: The session ended or replay was detected.
            SessionRefreshOriginNotAllowedFailure: A web request has no allowed Origin.
        """
        now = self._utc_now()
        state = await self._sessions.lock_session_by_refresh_token_hash(
            self._hash_refresh_token(refresh_token)
        )
        if state is None:
            await self._unit_of_work.commit()
            raise SessionRefreshTokenInvalidFailure

        # Every web-session refresh requires an allowed browser Origin, even if
        # a caller tries to move its cookie credential into the JSON body.
        if state.client_kind is ClientKind.WEB and not is_origin_allowed:
            await self._unit_of_work.commit()
            raise SessionRefreshOriginNotAllowedFailure

        # Account and expiry state ends the refresh before token-reuse decisions.
        is_ended = (
            state.session_revoked_at is not None
            or state.idle_expires_at <= now
            or state.absolute_expires_at <= now
            or state.token_expires_at <= now
            or state.is_user_suspended
            or state.is_user_pending_deletion
        )
        if is_ended:
            if state.session_revoked_at is None and state.is_user_suspended:
                await self._sessions.revoke_session_and_refresh_tokens(
                    state.session_id,
                    revoked_at=now,
                    reason=SessionRevocationReason.ACCOUNT_SUSPENDED,
                )
            elif state.session_revoked_at is None and state.is_user_pending_deletion:
                await self._sessions.revoke_session_and_refresh_tokens(
                    state.session_id,
                    revoked_at=now,
                    reason=SessionRevocationReason.ACCOUNT_DELETED,
                )
            await self._unit_of_work.commit()
            raise SessionRefreshSessionEndedFailure

        # A first use spends the token, slides idle expiry, and creates its child.
        if state.token_used_at is None and state.token_revoked_at is None:
            await self._sessions.mark_refresh_token_used(state.token_id, now)
            idle_expires_at = min(
                now + self._settings.idle_lifetime_for(is_persistent=state.is_persistent),
                state.absolute_expires_at,
            )
            await self._sessions.refresh_session(
                state.session_id, refreshed_at=now, idle_expires_at=idle_expires_at
            )
            token_pair = await self._issue_rotated_tokens.invoke(
                owner_id=state.owner_id,
                session_id=state.session_id,
                parent_token_id=state.token_id,
                role=state.role,
                client_kind=state.client_kind,
                is_persistent=state.is_persistent,
                issued_at=now,
                refresh_expires_at=idle_expires_at,
            )
            await self._unit_of_work.commit()
            return token_pair

        # One prompt retry may replace the still-unused child of a lost response.
        is_within_grace = (
            state.token_used_at is not None
            and now - state.token_used_at < self._settings.reuse_grace
            and state.token_revoked_at is None
        )
        if is_within_grace:
            child = await self._sessions.find_refresh_token_child(state.token_id)
            if child is not None and not child.is_used and not child.is_revoked:
                await self._sessions.revoke_refresh_token(child.id, now)
                token_pair = await self._issue_rotated_tokens.invoke(
                    owner_id=state.owner_id,
                    session_id=state.session_id,
                    parent_token_id=state.token_id,
                    role=state.role,
                    client_kind=state.client_kind,
                    is_persistent=state.is_persistent,
                    issued_at=now,
                    refresh_expires_at=state.idle_expires_at,
                )
                await self._unit_of_work.commit()
                return token_pair

        # Any other use of a spent or revoked token ends the whole family.
        await self._sessions.revoke_session_and_refresh_tokens(
            state.session_id,
            revoked_at=now,
            reason=SessionRevocationReason.REFRESH_TOKEN_REUSED,
        )
        await self._auth_events.create_auth_event(
            NewAuthEventDTO(
                owner_id=state.owner_id,
                event_type=AuthEventType.REFRESH_TOKEN_REUSED,
                details={"session_id": str(state.session_id)},
                occurred_at=now,
            )
        )
        await self._unit_of_work.commit()
        logger.warning("Refresh-token reuse ended session %s", state.session_id)
        raise SessionRefreshSessionEndedFailure
