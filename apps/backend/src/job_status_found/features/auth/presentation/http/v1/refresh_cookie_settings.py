"""Settings shared by version 1 auth refresh-cookie response helpers."""

from dataclasses import dataclass
from datetime import timedelta

REFRESH_COOKIE_PATH = "/v1/auth"
"""The narrow path shared by refresh and sign-out."""


@dataclass(frozen=True, slots=True)
class RefreshCookieSettings:
    """The presentation-only refresh-cookie contract."""

    name: str
    """The configured cookie name."""

    secure: bool
    """Whether browsers send it only over HTTPS."""

    persistent_max_age: timedelta
    """How long a persistent browser cookie remains stored."""
