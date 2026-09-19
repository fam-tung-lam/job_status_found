"""Storage of accounts."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.current_user import CurrentUser
from job_status_found.features.auth.application.dtos.user_registration import UserRegistration
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class UserRepository(Protocol):
    """Reads and writes accounts inside the caller's transaction."""

    async def create_unverified_user_unless_email_taken(
        self, registration: UserRegistration
    ) -> User | None:
        """Create an unverified account unless its normalized email already has one.

        Args:
            registration: The details of the new account.

        Returns:
            The new account, or `None` when an account with the same normalized
            email exists, including one another transaction just created.
        """
        ...

    async def lock_user_by_normalized_email(self, email_normalized: str) -> User | None:
        """Find the account of a normalized email and lock it until the transaction ends.

        Args:
            email_normalized: The NFKC, lower-case form of the address.

        Returns:
            The account, or `None` when no account has that email.
        """
        ...

    async def replace_first_and_last_name(
        self, owner_id: UUID, registration: UserRegistration
    ) -> None:
        """Replace an account's first and last name with those of a later sign-up.

        Args:
            owner_id: The account to update.
            registration: The details of the later sign-up; its email is not written.
        """
        ...

    async def set_email_verified_at(self, owner_id: UUID, verified_at: datetime) -> None:
        """Mark an account's email verified.

        Args:
            owner_id: The account whose mailbox was proved.
            verified_at: The timezone-aware verification instant.
        """
        ...

    async def find_current_user(self, owner_id: UUID) -> CurrentUser | None:
        """Find the owner's profile and linked sign-in methods.

        Args:
            owner_id: The authenticated account.

        Returns:
            The current-user projection, or `None` when the account is gone.
        """
        ...

    async def find_user_role(self, owner_id: UUID) -> UserRole | None:
        """Find an account's current role.

        Args:
            owner_id: The authenticated account.

        Returns:
            Its current `UserRole`, or `None` when the account is gone.
        """
        ...
