"""Create an initial password session and its credentials."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO
from job_status_found.features.auth.application.dtos.token_pair_dto import TokenPairDTO
from job_status_found.features.auth.application.ports.access_token_codec import AccessTokenCodec
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class IssuePasswordSessionSettings:
    """The configured access, idle, and absolute session lifetimes."""

    access_token_lifetime: timedelta
    """How long an access token works."""

    persistent_idle_lifetime: timedelta
    """The sliding idle lifetime of a persistent session."""

    persistent_absolute_lifetime: timedelta
    """The fixed absolute lifetime of a persistent session."""

    non_persistent_idle_lifetime: timedelta
    """The sliding idle lifetime of a non-persistent session."""

    non_persistent_absolute_lifetime: timedelta
    """The fixed absolute lifetime of a non-persistent session."""

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

    def absolute_lifetime_for(self, *, is_persistent: bool) -> timedelta:
        """Return the absolute lifetime selected by persistence.

        Args:
            is_persistent: Whether the session remembers the device.

        Returns:
            The configured fixed lifetime.
        """
        if is_persistent:
            return self.persistent_absolute_lifetime
        return self.non_persistent_absolute_lifetime


class IssuePasswordSessionUseCase:
    """Create a password session and its first access and refresh tokens."""

    def __init__(
        self,
        *,
        sessions: SessionRepository,
        access_tokens: AccessTokenCodec,
        generate_refresh_token: Callable[[], str],
        hash_refresh_token: Callable[[str], bytes],
        settings: IssuePasswordSessionSettings,
    ) -> None:
        """Keep the repository, codec, helpers, and session lifetimes.

        Args:
            sessions: Stores sessions and refresh-token families.
            access_tokens: Issues the short-lived access token.
            generate_refresh_token: Creates an opaque refresh credential.
            hash_refresh_token: Hashes the credential for storage.
            settings: The configured session lifetimes.
        """
        self._sessions = sessions
        self._access_tokens = access_tokens
        self._generate_refresh_token = generate_refresh_token
        self._hash_refresh_token = hash_refresh_token
        self._settings = settings

    async def invoke(
        self,
        owner_id: UUID,
        role: UserRole,
        session_input: SessionInputDTO,
        issued_at: datetime,
    ) -> TokenPairDTO:
        """Create an initial session and credentials without committing.

        The calling use case owns the transaction so it can commit the session
        with the authentication proof that opened it.

        Args:
            owner_id: The authenticated account.
            role: The role to place in the access token.
            session_input: The client choices and request facts to store.
            issued_at: The credential-proof instant.

        Returns:
            The credentials to present after the caller commits.
        """
        idle_expires_at = issued_at + self._settings.idle_lifetime_for(
            is_persistent=session_input.remember_me
        )
        absolute_expires_at = issued_at + self._settings.absolute_lifetime_for(
            is_persistent=session_input.remember_me
        )
        session_id = await self._sessions.create_session(
            owner_id,
            session_input,
            created_at=issued_at,
            idle_expires_at=idle_expires_at,
            absolute_expires_at=absolute_expires_at,
        )
        refresh_token = self._generate_refresh_token()
        await self._sessions.create_refresh_token(
            session_id,
            self._hash_refresh_token(refresh_token),
            parent_token_id=None,
            created_at=issued_at,
            expires_at=idle_expires_at,
        )
        access_token = self._access_tokens.issue_access_token(
            AccessTokenClaimsDTO(
                owner_id=owner_id,
                session_id=session_id,
                role=role,
                issued_at=issued_at,
            )
        )
        return TokenPairDTO(
            access_token=access_token,
            expires_in=int(self._settings.access_token_lifetime.total_seconds()),
            refresh_token=refresh_token,
            client_kind=session_input.client_kind,
            is_persistent=session_input.remember_me,
        )
