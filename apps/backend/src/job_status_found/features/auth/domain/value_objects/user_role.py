"""Instance-level roles carried by access tokens."""

from enum import StrEnum


class UserRole(StrEnum):
    """An account's instance-level authorization role."""

    USER = "user"
    """An ordinary product user."""

    ADMIN = "admin"
    """An administrator of the product instance."""
