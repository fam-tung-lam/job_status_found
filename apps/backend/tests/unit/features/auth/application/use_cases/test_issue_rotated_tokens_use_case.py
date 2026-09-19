"""Unit tests of rotated access and refresh-token issuance."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.application.ports.access_token_codec import AccessTokenCodec
from job_status_found.features.auth.application.ports.session_repository import SessionRepository
from job_status_found.features.auth.application.use_cases.issue_rotated_tokens_use_case import (
    IssueRotatedTokensSettings,
    IssueRotatedTokensUseCase,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed token-rotation instant."""


class TestIssueRotatedTokensUseCase:
    """Child refresh-token persistence and access-token claims."""

    @pytest.mark.asyncio
    async def test_rotation_stores_one_child_and_returns_its_clear_credential(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: an existing refresh-token family and a generated child credential.
        When: replacement credentials are issued.
        Then: the child hash and access-token claims use the existing session.
        """
        # Given: an existing refresh-token family and a generated child credential.
        sessions = mocker.create_autospec(SessionRepository, instance=True)
        access_tokens = mocker.create_autospec(AccessTokenCodec, instance=True)
        generate_refresh_token = mocker.stub(name="generate_refresh_token")
        hash_refresh_token = mocker.stub(name="hash_refresh_token")
        owner_id = uuid4()
        session_id = uuid4()
        parent_token_id = uuid4()
        refresh_expires_at = NOW + timedelta(days=30)
        generate_refresh_token.return_value = "clear-child-token"
        hash_refresh_token.return_value = b"child-token-hash"
        access_tokens.issue_access_token.return_value = "access-token"
        use_case = IssueRotatedTokensUseCase(
            sessions=sessions,
            access_tokens=access_tokens,
            generate_refresh_token=generate_refresh_token,
            hash_refresh_token=hash_refresh_token,
            settings=IssueRotatedTokensSettings(access_token_lifetime=timedelta(minutes=15)),
        )

        # When: replacement credentials are issued.
        result = await use_case.invoke(
            owner_id=owner_id,
            session_id=session_id,
            parent_token_id=parent_token_id,
            role=UserRole.USER,
            client_kind=ClientKind.ANDROID,
            is_persistent=True,
            issued_at=NOW,
            refresh_expires_at=refresh_expires_at,
        )

        # Then: the child hash and access-token claims use the existing session.
        sessions.create_refresh_token.assert_awaited_once_with(
            session_id,
            b"child-token-hash",
            parent_token_id=parent_token_id,
            created_at=NOW,
            expires_at=refresh_expires_at,
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
            result.access_token,
            result.expires_in,
            result.refresh_token,
            result.client_kind,
            result.is_persistent,
        ) == (
            "access-token",
            900,
            "clear-child-token",
            ClientKind.ANDROID,
            True,
        )
