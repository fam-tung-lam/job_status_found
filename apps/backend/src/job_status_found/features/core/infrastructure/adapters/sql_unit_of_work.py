"""The request's database transaction as a unit of work."""

from sqlalchemy.ext.asyncio import AsyncSession


class SqlUnitOfWork:
    """`UnitOfWork` that commits the request's database session."""

    def __init__(self, session: AsyncSession) -> None:
        """Commit the session every SQL repository of the operation shares.

        Args:
            session: The request's database session.
        """
        self._session = session

    async def commit(self) -> None:
        """Flush and commit every pending write of the session."""
        await self._session.commit()
