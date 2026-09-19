"""Unit tests of idempotent session sign-out."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.application.use_cases.sign_out_use_case import SignOutUseCase
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.entities.session_with_refresh_token import (
    SessionWithRefreshToken,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed sign-out instant."""


class TestSignOutUseCase:
    """Refresh-token precedence and durable idempotence."""

    @pytest.mark.asyncio
    async def test_a_refresh_token_takes_precedence_over_a_bearer_principal(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: both a refresh token and a bearer principal address sessions.
        When: sign-out runs.
        Then: only the refresh token's locked session is revoked and committed.
        """
        # Given: both credentials, with the refresh token resolving to a session.
        sessions = mocker.create_autospec(SessionRepository, instance=True)
        unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        hash_refresh_token = mocker.stub(name="hash_refresh_token")
        utc_now = mocker.stub(name="utc_now")
        hash_refresh_token.return_value = b"hash"
        utc_now.return_value = NOW
        state = SessionWithRefreshToken(
            session_id=uuid4(),
            owner_id=uuid4(),
            role=UserRole.USER,
            client_kind=ClientKind.WEB,
            is_persistent=False,
            is_user_suspended=False,
            is_user_pending_deletion=False,
            idle_expires_at=NOW,
            absolute_expires_at=NOW,
            session_revoked_at=None,
            token_id=uuid4(),
            token_expires_at=NOW,
            token_used_at=None,
            token_revoked_at=None,
        )
        sessions.lock_session_by_refresh_token_hash.return_value = state
        principal = AuthenticatedPrincipal(uuid4(), uuid4(), UserRole.USER)
        use_case = SignOutUseCase(
            sessions=sessions,
            unit_of_work=unit_of_work,
            hash_refresh_token=hash_refresh_token,
            utc_now=utc_now,
        )

        # When: sign-out runs.
        await use_case.invoke(refresh_token="refresh", principal=principal)

        # Then: only the refresh token's session is revoked and committed.
        sessions.lock_session_by_id.assert_not_awaited()
        sessions.revoke_session_and_refresh_tokens.assert_awaited_once_with(
            state.session_id, revoked_at=NOW, reason="signed_out"
        )
        unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_an_invalid_refresh_token_falls_back_to_the_valid_bearer_session(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: an unknown refresh token and a valid bearer principal.
        When: sign-out runs.
        Then: it locks and revokes the bearer session instead of doing nothing.
        """
        # Given: an unknown refresh token and a valid bearer principal.
        sessions = mocker.create_autospec(SessionRepository, instance=True)
        unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        hash_refresh_token = mocker.stub(name="hash_refresh_token")
        utc_now = mocker.stub(name="utc_now")
        hash_refresh_token.return_value = b"unknown-hash"
        utc_now.return_value = NOW
        sessions.lock_session_by_refresh_token_hash.return_value = None
        sessions.lock_session_by_id.return_value = True
        principal = AuthenticatedPrincipal(uuid4(), uuid4(), UserRole.USER)
        use_case = SignOutUseCase(
            sessions=sessions,
            unit_of_work=unit_of_work,
            hash_refresh_token=hash_refresh_token,
            utc_now=utc_now,
        )

        # When: sign-out runs.
        await use_case.invoke(refresh_token="stale", principal=principal)

        # Then: it locks and revokes the bearer session instead of doing nothing.
        sessions.lock_session_by_id.assert_awaited_once_with(
            principal.user_id, principal.session_id
        )
        sessions.revoke_session_and_refresh_tokens.assert_awaited_once_with(
            principal.session_id, revoked_at=NOW, reason="signed_out"
        )
        unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_a_known_spent_refresh_token_still_revokes_its_session(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: a recognized refresh token was already used and no bearer is supplied.
        When: sign-out runs.
        Then: its owning session is still revoked and the result is committed.
        """
        # Given: a recognized spent refresh token without a bearer credential.
        sessions = mocker.create_autospec(SessionRepository, instance=True)
        unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        hash_refresh_token = mocker.stub(name="hash_refresh_token")
        utc_now = mocker.stub(name="utc_now")
        hash_refresh_token.return_value = b"spent-hash"
        utc_now.return_value = NOW
        state = SessionWithRefreshToken(
            session_id=uuid4(),
            owner_id=uuid4(),
            role=UserRole.USER,
            client_kind=ClientKind.WEB,
            is_persistent=False,
            is_user_suspended=False,
            is_user_pending_deletion=False,
            idle_expires_at=NOW,
            absolute_expires_at=NOW,
            session_revoked_at=None,
            token_id=uuid4(),
            token_expires_at=NOW,
            token_used_at=NOW,
            token_revoked_at=None,
        )
        sessions.lock_session_by_refresh_token_hash.return_value = state
        use_case = SignOutUseCase(
            sessions=sessions,
            unit_of_work=unit_of_work,
            hash_refresh_token=hash_refresh_token,
            utc_now=utc_now,
        )

        # When: sign-out runs.
        await use_case.invoke(refresh_token="spent", principal=None)

        # Then: its owning session is still revoked and the result is committed.
        sessions.lock_session_by_id.assert_not_awaited()
        sessions.revoke_session_and_refresh_tokens.assert_awaited_once_with(
            state.session_id, revoked_at=NOW, reason="signed_out"
        )
        unit_of_work.commit.assert_awaited_once()
