"""Unit tests of refresh rotation and replay detection."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.token_pair_dto import TokenPairDTO
from job_status_found.features.auth.application.ports.auth_event_repository import (
    AuthEventRepository,
)
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.application.use_cases.issue_rotated_tokens_use_case import (
    IssueRotatedTokensUseCase,
)
from job_status_found.features.auth.application.use_cases.refresh_session_use_case import (
    RefreshSessionUseCase,
    SessionRefreshSettings,
)
from job_status_found.features.auth.domain.entities.session_with_refresh_token import (
    RefreshTokenChild,
    SessionWithRefreshToken,
)
from job_status_found.features.auth.domain.failures.session_refresh_failure import (
    SessionRefreshOriginNotAllowedFailure,
    SessionRefreshSessionEndedFailure,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed refresh instant."""


class TestRefreshSessionUseCase:
    """First rotation, lost-response grace, browser origin, and replay."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Build a refresh operation with fresh mocks."""
        self.sessions = mocker.create_autospec(SessionRepository, instance=True)
        self.auth_events = mocker.create_autospec(AuthEventRepository, instance=True)
        self.issue_rotated_tokens = mocker.create_autospec(IssueRotatedTokensUseCase, instance=True)
        self.unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        self.hash_refresh_token = mocker.stub(name="hash_refresh_token")
        self.utc_now = mocker.stub(name="utc_now")
        self.hash_refresh_token.return_value = b"token-hash"
        self.utc_now.return_value = NOW
        self.token_pair = TokenPairDTO(
            access_token="access",
            expires_in=900,
            refresh_token="child",
            client_kind=ClientKind.ANDROID,
            is_persistent=True,
        )
        self.issue_rotated_tokens.invoke.return_value = self.token_pair
        self.state = SessionWithRefreshToken(
            session_id=uuid4(),
            owner_id=uuid4(),
            role=UserRole.USER,
            client_kind=ClientKind.ANDROID,
            is_persistent=True,
            is_user_suspended=False,
            is_user_pending_deletion=False,
            idle_expires_at=NOW + timedelta(days=1),
            absolute_expires_at=NOW + timedelta(days=2),
            session_revoked_at=None,
            token_id=uuid4(),
            token_expires_at=NOW + timedelta(days=1),
            token_used_at=None,
            token_revoked_at=None,
        )
        self.sessions.lock_session_by_refresh_token_hash.return_value = self.state
        self.use_case = RefreshSessionUseCase(
            sessions=self.sessions,
            auth_events=self.auth_events,
            issue_rotated_tokens=self.issue_rotated_tokens,
            unit_of_work=self.unit_of_work,
            hash_refresh_token=self.hash_refresh_token,
            utc_now=self.utc_now,
            settings=SessionRefreshSettings(
                persistent_idle_lifetime=timedelta(days=30),
                non_persistent_idle_lifetime=timedelta(days=1),
                reuse_grace=timedelta(seconds=10),
            ),
        )

    @pytest.mark.asyncio
    async def test_first_rotation_spends_the_token_and_clamps_idle_to_absolute_expiry(
        self,
    ) -> None:
        """
        Given: an unused token whose absolute session expiry is before the next idle expiry.
        When: the token refreshes.
        Then: it is spent and the session idle expiry clamps to the absolute expiry.
        """
        # Given: an unused token whose absolute expiry is the earlier bound.
        # When: the token refreshes.
        result = await self.use_case.invoke("parent", is_origin_allowed=False)

        # Then: it is spent and the session idle expiry clamps to the absolute expiry.
        assert result == self.token_pair
        self.sessions.mark_refresh_token_used.assert_awaited_once_with(self.state.token_id, NOW)
        self.sessions.refresh_session.assert_awaited_once_with(
            self.state.session_id,
            refreshed_at=NOW,
            idle_expires_at=self.state.absolute_expires_at,
        )
        self.unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_a_retry_strictly_inside_grace_revokes_the_unused_child_and_replaces_it(
        self,
    ) -> None:
        """
        Given: a token used just under ten seconds ago with an unused child.
        When: the parent is retried.
        Then: the lost child is revoked and a sibling replaces it without ending the session.
        """
        # Given: a token used just under ten seconds ago with an unused child.
        self.state = replace(
            self.state,
            token_used_at=NOW - timedelta(seconds=10) + timedelta(microseconds=1),
        )
        self.sessions.lock_session_by_refresh_token_hash.return_value = self.state
        child = RefreshTokenChild(id=uuid4(), is_used=False, is_revoked=False)
        self.sessions.find_refresh_token_child.return_value = child

        # When: the parent is retried.
        result = await self.use_case.invoke("parent", is_origin_allowed=False)

        # Then: the lost child is revoked and a sibling replaces it.
        assert result == self.token_pair
        self.sessions.revoke_refresh_token.assert_awaited_once_with(child.id, NOW)
        self.sessions.revoke_session_and_refresh_tokens.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_a_retry_at_the_grace_boundary_revokes_the_family_and_records_reuse(
        self,
    ) -> None:
        """
        Given: a token used exactly ten seconds ago.
        When: the parent is replayed.
        Then: grace no longer applies and the session is revoked before rejection.
        """
        # Given: a token used exactly ten seconds ago.
        self.state = replace(self.state, token_used_at=NOW - timedelta(seconds=10))
        self.sessions.lock_session_by_refresh_token_hash.return_value = self.state

        # When: the parent is replayed.
        # Then: the family and audit event commit before session_ended.
        with pytest.raises(SessionRefreshSessionEndedFailure):
            await self.use_case.invoke("parent", is_origin_allowed=False)
        self.sessions.revoke_session_and_refresh_tokens.assert_awaited_once_with(
            self.state.session_id, revoked_at=NOW, reason="refresh_token_reused"
        )
        self.auth_events.create_auth_event.assert_awaited_once()
        self.unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_a_web_session_without_an_allowed_origin_is_rejected_before_rotation(
        self,
    ) -> None:
        """
        Given: an unused refresh token belonging to a web session.
        When: it is submitted without an allowed Origin.
        Then: the request is rejected without spending the token.
        """
        # Given: an unused refresh token belonging to a web session.
        self.state = replace(self.state, client_kind=ClientKind.WEB)
        self.sessions.lock_session_by_refresh_token_hash.return_value = self.state

        # When: it is submitted without an allowed Origin.
        # Then: the request is rejected without spending the token.
        with pytest.raises(SessionRefreshOriginNotAllowedFailure):
            await self.use_case.invoke("parent", is_origin_allowed=False)
        self.sessions.mark_refresh_token_used.assert_not_awaited()
        self.unit_of_work.commit.assert_awaited_once()

    @pytest.mark.parametrize(
        ("ended_state", "expected_revocation_reason"),
        [
            ("revoked", None),
            ("idle-expired", None),
            ("absolute-expired", None),
            ("suspended", "account_suspended"),
            ("pending-deletion", "account_deleted"),
        ],
    )
    @pytest.mark.asyncio
    async def test_every_ended_session_state_commits_before_session_ended(
        self, ended_state: str, expected_revocation_reason: str | None
    ) -> None:
        """
        Given: a revoked, expired, suspended, or pending-deletion session.
        When: its refresh token is submitted.
        Then: session_ended follows the state-specific durable effect.
        """
        # Given: one ended session state.
        match ended_state:
            case "revoked":
                self.state = replace(self.state, session_revoked_at=NOW)
            case "idle-expired":
                self.state = replace(self.state, idle_expires_at=NOW)
            case "absolute-expired":
                self.state = replace(self.state, absolute_expires_at=NOW)
            case "suspended":
                self.state = replace(self.state, is_user_suspended=True)
            case "pending-deletion":
                self.state = replace(self.state, is_user_pending_deletion=True)
            case _:
                pytest.fail(f"Unknown ended state {ended_state}.")
        self.sessions.lock_session_by_refresh_token_hash.return_value = self.state

        # When: its refresh token is submitted.
        # Then: session_ended follows the state-specific durable effect.
        with pytest.raises(SessionRefreshSessionEndedFailure):
            await self.use_case.invoke("token", is_origin_allowed=True)
        if expected_revocation_reason is None:
            self.sessions.revoke_session_and_refresh_tokens.assert_not_awaited()
        else:
            self.sessions.revoke_session_and_refresh_tokens.assert_awaited_once_with(
                self.state.session_id,
                revoked_at=NOW,
                reason=expected_revocation_reason,
            )
        self.unit_of_work.commit.assert_awaited_once()
