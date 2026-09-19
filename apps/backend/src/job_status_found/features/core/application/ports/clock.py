"""The current time."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Tells the current instant, replaceable so tests control expiry."""

    def now(self) -> datetime:
        """Read the current instant.

        Returns:
            A timezone-aware instant.
        """
        ...
