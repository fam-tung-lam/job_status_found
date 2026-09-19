"""Security-event types stored by the auth feature."""

from enum import StrEnum


class AuthEventType(StrEnum):
    """A security-relevant event written to the audit stream."""

    EXISTING_ACCOUNT_NOTICE_SENT = "existing_account_notice_sent"
    """A verified account owner received a duplicate sign-up notice."""

    SIGN_IN_FAILED = "sign_in_failed"
    """A password sign-in proof failed."""

    EMAIL_VERIFICATION_FAILED = "email_verification_failed"
    """An email verification proof failed."""

    REFRESH_TOKEN_REUSED = "refresh_token_reused"  # noqa: S105 - audit vocabulary
    """A spent refresh token was presented outside the retry grace."""
