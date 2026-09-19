"""Read the signed-in account's current profile and sign-in methods."""

from uuid import UUID

from job_status_found.features.auth.application.dtos.current_user import CurrentUser
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.domain.failures.access_token_authentication_failure import (
    AccessTokenAuthenticationFailure,
)


class GetCurrentUserUseCase:
    """Return the account represented by an authenticated principal."""

    def __init__(self, *, users: UserRepository) -> None:
        """Keep the account repository.

        Args:
            users: Reads the owner's profile and sign-in methods.
        """
        self._users = users

    async def invoke(self, owner_id: UUID) -> CurrentUser:
        """Read the current user.

        Args:
            owner_id: The authenticated account id.

        Returns:
            The current profile and linked sign-in methods.

        Raises:
            AccessTokenAuthenticationFailure: The token's account no longer exists.
        """
        current_user = await self._users.find_current_user(owner_id)
        if current_user is None:
            raise AccessTokenAuthenticationFailure
        return current_user
