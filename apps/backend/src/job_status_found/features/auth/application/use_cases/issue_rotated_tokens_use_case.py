"""Issue replacement access and refresh tokens for an existing session."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from job_status_found.features.auth.application.dtos.access_token_claims import (
    AccessTokenClaims,
)
from job_status_found.features.auth.application.dtos.token_pair import TokenPair
from job_status_found.features.auth.application.ports.access_token_codec import AccessTokenCodec
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


@dataclass(frozen=True, slots=True)
class IssueRotatedTokensSettings:
    """The configured access-token lifetime."""

    access_token_lifetime: timedelta
    """How long an access token works."""


class IssueRotatedTokensUseCase:
    """Issue a child refresh token and access token for an existing session."""

    def __init__(
        self,
        *,
        sessions: SessionRepository,
        access_tokens: AccessTokenCodec,
        generate_refresh_token: Callable[[], str],
        hash_refresh_token: Callable[[str], bytes],
        settings: IssueRotatedTokensSettings,
    ) -> None:
        """Keep the repository, codec, helpers, and access-token lifetime.

        Args:
            sessions: Stores the child refresh token.
            access_tokens: Issues the short-lived access token.
            generate_refresh_token: Creates an opaque refresh credential.
            hash_refresh_token: Hashes the credential for storage.
            settings: The configured access-token lifetime.
        """
        self._sessions = sessions
        self._access_tokens = access_tokens
        self._generate_refresh_token = generate_refresh_token
        self._hash_refresh_token = hash_refresh_token
        self._settings = settings

    async def invoke(
        self,
        *,
        owner_id: UUID,
        session_id: UUID,
        parent_token_id: UUID,
        role: UserRole,
        client_kind: ClientKind,
        is_persistent: bool,
        issued_at: datetime,
        refresh_expires_at: datetime,
    ) -> TokenPair:
        """Issue replacement credentials without committing.

        The calling refresh use case owns the transaction so token rotation is
        committed atomically with the refresh-family state changes.

        Args:
            owner_id: The session owner.
            session_id: The existing session.
            parent_token_id: The spent token this child replaces.
            role: The account's current role.
            client_kind: The session's fixed client kind.
            is_persistent: Whether the session remembers the device.
            issued_at: When this rotation happened.
            refresh_expires_at: The child's expiry copied from the session.

        Returns:
            The replacement credentials.
        """
        refresh_token = self._generate_refresh_token()
        await self._sessions.create_refresh_token(
            session_id,
            self._hash_refresh_token(refresh_token),
            parent_token_id=parent_token_id,
            created_at=issued_at,
            expires_at=refresh_expires_at,
        )
        access_token = self._access_tokens.issue_access_token(
            AccessTokenClaims(
                owner_id=owner_id,
                session_id=session_id,
                role=role,
                issued_at=issued_at,
            )
        )
        return TokenPair(
            access_token=access_token,
            expires_in=int(self._settings.access_token_lifetime.total_seconds()),
            refresh_token=refresh_token,
            client_kind=client_kind,
            is_persistent=is_persistent,
        )
