"""The operating system's clock."""

from datetime import UTC, datetime


class SystemClock:
    """`Clock` that reads the real time in UTC."""

    def now(self) -> datetime:
        """Read the current instant.

        Returns:
            The current time in UTC.
        """
        return datetime.now(UTC)
