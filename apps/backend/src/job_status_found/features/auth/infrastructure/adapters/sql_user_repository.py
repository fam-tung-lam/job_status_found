"""Accounts in the PostgreSQL `users` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.dtos.current_user_dto import CurrentUserDTO
from job_status_found.features.auth.application.dtos.user_registration_dto import (
    UserRegistrationDTO,
)
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.value_objects.identity_provider import IdentityProvider
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.auth.infrastructure.db.tables import (
    ExternalIdentityTable,
    PasswordCredentialTable,
    UserTable,
)


class SqlUserRepository:
    """`UserRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request's database session; the use case commits it.
        """
        self._session = session

    async def create_unverified_user_unless_email_taken(
        self, registration: UserRegistrationDTO
    ) -> User | None:
        """Create an unverified account unless its normalized email already has one.

        The insert waits for a concurrent transaction that holds the same
        normalized email, so two simultaneous sign-ups never both create one.

        Args:
            registration: The details of the new account.

        Returns:
            The new account, or `None` when the normalized email already has one.
        """
        # Insert the account, or nothing when the normalized email is taken. The
        # unique index makes a concurrent insert of the same email wait here.
        statement = (
            insert(UserTable)
            .values(
                {
                    UserTable.email: registration.email.as_typed,
                    UserTable.email_normalized: registration.email.normalized,
                    UserTable.first_name: registration.first_name,
                    UserTable.last_name: registration.last_name,
                    UserTable.role: UserRole.USER.value,
                    UserTable.created_at: registration.registered_at,
                    UserTable.updated_at: registration.registered_at,
                }
            )
            .on_conflict_do_nothing(index_elements=[UserTable.email_normalized])
            .returning(UserTable.id)
        )
        user_id = await self._session.scalar(statement)

        # No returned id means the insert did nothing because the email is taken.
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
            select(UserTable)
            .where(UserTable.email_normalized == email_normalized)
            .with_for_update()
        )
        row = await self._session.scalar(statement)
        if row is None:
            return None
        return self._to_user(row)

    async def replace_first_and_last_name(
        self, owner_id: UUID, registration: UserRegistrationDTO
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

    async def set_email_verified_at(self, owner_id: UUID, verified_at: datetime) -> None:
        """Mark an account's email verified.

        Args:
            owner_id: The account whose mailbox was proved.
            verified_at: The verification instant.
        """
        await self._session.execute(
            update(UserTable)
            .where(UserTable.id == owner_id)
            .values(
                {
                    UserTable.email_verified_at: verified_at,
                    UserTable.updated_at: verified_at,
                }
            )
        )

    async def find_current_user(self, owner_id: UUID) -> CurrentUserDTO | None:
        """Find the owner's profile and linked sign-in methods.

        Args:
            owner_id: The authenticated account.

        Returns:
            The current-user projection, or `None` when the account is gone.
        """
        row = await self._session.scalar(select(UserTable).where(UserTable.id == owner_id))
        if row is None:
            return None
        has_password = (
            await self._session.scalar(
                select(PasswordCredentialTable.user_id).where(
                    PasswordCredentialTable.user_id == owner_id
                )
            )
            is not None
        )
        stored_providers = await self._session.scalars(
            select(ExternalIdentityTable.provider)
            .where(ExternalIdentityTable.user_id == owner_id)
            .order_by(ExternalIdentityTable.provider)
        )
        linked_providers = tuple(IdentityProvider(provider) for provider in stored_providers)
        return CurrentUserDTO(
            id=row.id,
            email=row.email,
            first_name=row.first_name,
            last_name=row.last_name,
            avatar_url=row.avatar_url,
            locale=row.locale,
            role=UserRole(row.role),
            has_password=has_password,
            linked_providers=linked_providers,
        )

    async def find_user_role(self, owner_id: UUID) -> UserRole | None:
        """Find an account's current role.

        Args:
            owner_id: The authenticated account.

        Returns:
            Its current role, or `None` when the account is gone.
        """
        role = await self._session.scalar(select(UserTable.role).where(UserTable.id == owner_id))
        return None if role is None else UserRole(role)

    @staticmethod
    def _to_user(row: UserTable) -> User:
        """Map one stored row to the auth domain entity.

        Args:
            row: The mapped account row.

        Returns:
            The account entity.
        """
        return User(
            id=row.id,
            email=row.email,
            email_verified_at=row.email_verified_at,
            first_name=row.first_name,
            last_name=row.last_name,
            avatar_url=row.avatar_url,
            locale=row.locale,
            role=UserRole(row.role),
            suspended_at=row.suspended_at,
            deletion_requested_at=row.deletion_requested_at,
        )
