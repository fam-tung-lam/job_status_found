"""Unit tests of requiring an account's current stored role."""

from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.application.use_cases.require_user_role_use_case import (
    RequireUserRoleUseCase,
)
from job_status_found.features.auth.domain.failures.required_user_role_not_granted_failure import (
    RequiredUserRoleNotGrantedFailure,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class TestRequireUserRoleUseCase:
    """Role authorization from storage rather than the access-token claim."""

    @pytest.mark.asyncio
    async def test_a_different_stored_role_is_rejected(self, mocker: MockerFixture) -> None:
        """
        Given: storage says the account is a user.
        When: an admin role is required.
        Then: authorization is rejected from current state.
        """
        # Given: storage says the account is a user.
        users = mocker.create_autospec(UserRepository, instance=True)
        users.find_user_role.return_value = UserRole.USER

        # When: an admin role is required.
        # Then: authorization is rejected from current state.
        with pytest.raises(RequiredUserRoleNotGrantedFailure):
            await RequireUserRoleUseCase(users=users).invoke(uuid4(), UserRole.ADMIN)
