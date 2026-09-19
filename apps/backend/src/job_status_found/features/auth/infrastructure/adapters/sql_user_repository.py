"""Accounts in the PostgreSQL `users` table."""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.user_registration import UserRegistration
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.infrastructure.db.tables import UserTable

_NEW_USER_ROLE = "user"
"""Instance role every new account gets; only an admin tool may grant `admin`."""


class SqlUserRepository:
    """`UserRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request's database session; the use case commits it.
        """
        self._session = session

    async def create_unverified_user_unless_email_taken(
        self, registration: UserRegistration
    ) -> User | None:
        """Create an unverified account unless its normalized email already has one.

        The insert waits for a concurrent transaction that holds the same
        normalized email, so two simultaneous sign-ups never both create one.

        Args:
            registration: The details of the new account.

        Returns:
            The new account, or `None` when the normalized email already has one.
        """
        statement = (
            insert(UserTable)
            .values(
                {
                    UserTable.email: registration.email.as_typed,
                    UserTable.email_normalized: registration.email.normalized,
                    UserTable.first_name: registration.first_name,
                    UserTable.last_name: registration.last_name,
                    UserTable.role: _NEW_USER_ROLE,
                    UserTable.created_at: registration.registered_at,
                    UserTable.updated_at: registration.registered_at,
                }
            )
            .on_conflict_do_nothing(index_elements=[UserTable.email_normalized])
            .returning(UserTable.id)
        )
        user_id = await self._session.scalar(statement)
        if user_id is None:
            return None
        return User(id=user_id, email=registration.email.as_typed, email_verified_at=None)

    async def lock_user_by_normalized_email(self, email_normalized: str) -> User | None:
        """Find the account of a normalized email and lock it until the transaction ends.

        Args:
            email_normalized: The NFKC, lower-case form of the address.

        Returns:
            The account, or `None` when no account has that email.
        """
        statement = (
            select(UserTable.id, UserTable.email, UserTable.email_verified_at)
            .where(UserTable.email_normalized == email_normalized)
            .with_for_update()
        )
        row = (await self._session.execute(statement)).one_or_none()
        if row is None:
            return None
        return User(id=row.id, email=row.email, email_verified_at=row.email_verified_at)

    async def replace_first_and_last_name(
        self, owner_id: UUID, registration: UserRegistration
    ) -> None:
        """Replace an account's first and last name with those of a later sign-up.

        Args:
            owner_id: The account to update.
            registration: The details of the later sign-up; its email is not written.
        """
        await self._session.execute(
            update(UserTable)
            .where(UserTable.id == owner_id)
            .values(
                {
                    UserTable.first_name: registration.first_name,
                    UserTable.last_name: registration.last_name,
                    UserTable.updated_at: registration.registered_at,
                }
            )
        )
