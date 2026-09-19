"""Reasons why an authenticated session can end."""

from enum import StrEnum


class SessionRevocationReason(StrEnum):
    """A durable reason stored with a revoked session."""

    SIGNED_OUT = "signed_out"
    """The owner explicitly signed out."""

    REVOKED_BY_USER = "revoked_by_user"
    """The owner revoked the session from session management."""

    PASSWORD_CHANGED = "password_changed"  # noqa: S105 - revocation vocabulary
    """A password change invalidated the session."""

    REFRESH_TOKEN_REUSED = "refresh_token_reused"  # noqa: S105 - revocation vocabulary
    """Refresh-token replay ended the token family."""

    ACCOUNT_SUSPENDED = "account_suspended"
    """Account suspension ended the session."""

    ACCOUNT_DELETED = "account_deleted"
    """Account deletion ended the session."""
