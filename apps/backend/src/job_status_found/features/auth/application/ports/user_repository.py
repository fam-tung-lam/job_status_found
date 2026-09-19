"""Storage of accounts."""

from typing import Protocol
from uuid import UUID

from job_status_found.features.auth.application.dtos.user_registration import UserRegistration
from job_status_found.features.auth.domain.entities.user import User


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

    async def replace_name_and_accepted_terms(
        self, owner_id: UUID, registration: UserRegistration
    ) -> None:
        """Replace an account's name and accepted terms with those of a later sign-up.

        Args:
            owner_id: The account to update.
            registration: The details of the later sign-up; its email is not written.
        """
        ...
