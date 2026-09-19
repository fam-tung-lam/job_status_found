"""The current time from the operating system's clock."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Read the current instant.

    Use cases receive this function by injection, so a test can stub the time.

    Returns:
        The current time in UTC.
    """
    return datetime.now(UTC)
