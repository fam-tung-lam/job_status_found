"""Require an account's stored role for a sensitive authorization decision."""

from uuid import UUID

from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class RequiredUserRoleNotGranted(Exception):
    """The account's stored role does not grant the requested operation."""


class RequireUserRoleUseCase:
    """Decide a role requirement from current database state, not a JWT claim."""

    def __init__(self, *, users: UserRepository) -> None:
        """Keep the account repository.

        Args:
            users: Reads the account's stored role.
        """
        self._users = users

    async def invoke(self, owner_id: UUID, required_role: UserRole) -> None:
        """Require the account's current stored role.

        Args:
            owner_id: The authenticated account.
            required_role: The role needed by the operation.

        Raises:
            RequiredUserRoleNotGranted: The account is missing or has another role.
        """
        if await self._users.find_user_role(owner_id) is not required_role:
            raise RequiredUserRoleNotGranted
