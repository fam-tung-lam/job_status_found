"""Methods that can prove an account during sign-in."""

from enum import StrEnum


class SignInMethod(StrEnum):
    """A credential source recorded on an authenticated session."""

    PASSWORD = "password"  # noqa: S105 - sign-in method vocabulary
    """The account's password."""

    GOOGLE = "google"
    """Google OpenID Connect."""
