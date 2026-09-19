"""Unit tests of initial password-session issuance."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO
from job_status_found.features.auth.application.ports.access_token_codec import AccessTokenCodec
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.application.use_cases.issue_password_session_use_case import (
    IssuePasswordSessionSettings,
    IssuePasswordSessionUseCase,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed initial-session issue instant."""


class TestIssuePasswordSessionUseCase:
    """Persistence-specific initial session lifetimes and token storage."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("is_persistent", "idle_lifetime", "absolute_lifetime"),
        [
            (True, timedelta(days=30), timedelta(days=180)),
            (False, timedelta(days=1), timedelta(days=7)),
        ],
        ids=["persistent", "non-persistent"],
    )
    async def test_initial_session_uses_the_lifetimes_selected_by_persistence(
        self,
        mocker: MockerFixture,
        is_persistent: bool,
        idle_lifetime: timedelta,
        absolute_lifetime: timedelta,
    ) -> None:
        """
        Given: distinct persistent and non-persistent lifetime settings.
        When: an initial password session is issued.
        Then: its idle, absolute, and first refresh expiries use the selected settings.
        """
        # Given: distinct persistent and non-persistent lifetime settings.
        sessions = mocker.create_autospec(SessionRepository, instance=True)
        access_tokens = mocker.create_autospec(AccessTokenCodec, instance=True)
        generate_refresh_token = mocker.stub(name="generate_refresh_token")
        hash_refresh_token = mocker.stub(name="hash_refresh_token")
        owner_id = uuid4()
        session_id = uuid4()
        session_input = SessionInputDTO(
            client_kind=ClientKind.WEB,
            remember_me=is_persistent,
            ip_address=None,
            user_agent="test",
        )
        sessions.create_session.return_value = session_id
        generate_refresh_token.return_value = "clear-refresh-token"
        hash_refresh_token.return_value = b"refresh-token-hash"
        access_tokens.issue_access_token.return_value = "access-token"
        use_case = IssuePasswordSessionUseCase(
            sessions=sessions,
            access_tokens=access_tokens,
            generate_refresh_token=generate_refresh_token,
            hash_refresh_token=hash_refresh_token,
            settings=IssuePasswordSessionSettings(
                access_token_lifetime=timedelta(minutes=15),
                persistent_idle_lifetime=timedelta(days=30),
                persistent_absolute_lifetime=timedelta(days=180),
                non_persistent_idle_lifetime=timedelta(days=1),
                non_persistent_absolute_lifetime=timedelta(days=7),
            ),
        )

        # When: an initial password session is issued.
        result = await use_case.invoke(owner_id, UserRole.USER, session_input, NOW)

        # Then: its idle, absolute, and first refresh expiries use the selected settings.
        sessions.create_session.assert_awaited_once_with(
            owner_id,
            session_input,
            created_at=NOW,
            idle_expires_at=NOW + idle_lifetime,
            absolute_expires_at=NOW + absolute_lifetime,
        )
        sessions.create_refresh_token.assert_awaited_once_with(
            session_id,
            b"refresh-token-hash",
            parent_token_id=None,
            created_at=NOW,
            expires_at=NOW + idle_lifetime,
        )
        access_tokens.issue_access_token.assert_called_once_with(
            AccessTokenClaimsDTO(
                owner_id=owner_id,
                session_id=session_id,
                role=UserRole.USER,
                issued_at=NOW,
            )
        )
        assert (
            result.expires_in,
            result.refresh_token,
            result.is_persistent,
        ) == (900, "clear-refresh-token", is_persistent)
