"""Unit tests of reading the authenticated account."""

from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.current_user import CurrentUser
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.application.use_cases.get_current_user_use_case import (
    GetCurrentUserUseCase,
)
from job_status_found.features.auth.domain.failures.access_token_authentication_failure import (
    AccessTokenAuthenticationFailure,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class TestGetCurrentUserUseCase:
    """Owner-scoped profile lookup and a deleted-token subject."""

    @pytest.mark.asyncio
    async def test_the_owner_profile_is_returned(self, mocker: MockerFixture) -> None:
        """
        Given: the authenticated account still exists.
        When: its current profile is read.
        Then: the repository projection is returned.
        """
        # Given: the authenticated account still exists.
        users = mocker.create_autospec(UserRepository, instance=True)
        current_user = CurrentUser(
            id=uuid4(),
            email="jane@example.com",
            first_name="Jane",
            last_name="Doe",
            avatar_url=None,
            locale=None,
            role=UserRole.USER,
            has_password=True,
            linked_providers=(),
        )
        users.find_current_user.return_value = current_user

        # When: its current profile is read.
        result = await GetCurrentUserUseCase(users=users).invoke(current_user.id)

        # Then: the repository projection is returned.
        assert result == current_user

    @pytest.mark.asyncio
    async def test_a_deleted_token_subject_is_rejected(self, mocker: MockerFixture) -> None:
        """
        Given: the access token's account has been deleted.
        When: its current profile is read.
        Then: the token is treated as invalid.
        """
        # Given: the access token's account has been deleted.
        users = mocker.create_autospec(UserRepository, instance=True)
        users.find_current_user.return_value = None

        # When: its current profile is read.
        # Then: the token is treated as invalid.
        with pytest.raises(AccessTokenAuthenticationFailure):
            await GetCurrentUserUseCase(users=users).invoke(uuid4())
