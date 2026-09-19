"""Password hashes in the PostgreSQL `password_credentials` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.infrastructure.db.tables import PasswordCredentialTable


class SqlPasswordCredentialRepository:
    """`PasswordCredentialRepository` on the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Work inside the session's transaction.

        Args:
            session: The request's database session; the use case commits it.
        """
        self._session = session

    async def set_password_hash(
        self, owner_id: UUID, password_hash: str, changed_at: datetime
    ) -> None:
        """Set a user's password hash, adding the credential when the user has none.

        Args:
            owner_id: The user whose password this is.
            password_hash: The Argon2id PHC string; never the password itself.
            changed_at: When the password was set.
        """
        statement = insert(PasswordCredentialTable).values(
            {
                PasswordCredentialTable.user_id: owner_id,
                PasswordCredentialTable.password_hash: password_hash,
                PasswordCredentialTable.created_at: changed_at,
                PasswordCredentialTable.updated_at: changed_at,
            }
        )
        await self._session.execute(
            statement.on_conflict_do_update(
                index_elements=[PasswordCredentialTable.user_id],
                set_={
                    PasswordCredentialTable.password_hash: statement.excluded.password_hash,
                    PasswordCredentialTable.updated_at: statement.excluded.updated_at,
                },
            )
        )
