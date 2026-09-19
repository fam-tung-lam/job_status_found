"""The transaction every repository of one operation writes into."""

from typing import Protocol


class UnitOfWork(Protocol):
    """Commits the writes of every repository an operation used."""

    async def commit(self) -> None:
        """Make every write of the operation durable at once."""
        ...
