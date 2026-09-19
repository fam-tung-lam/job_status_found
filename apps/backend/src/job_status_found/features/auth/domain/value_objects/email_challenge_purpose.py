"""What an emailed code or link proves."""

from enum import StrEnum


class EmailChallengePurpose(StrEnum):
    """The closed vocabulary of `email_challenges.purpose`."""

    VERIFY_EMAIL = "verify_email"
    """A 6-digit code that proves control of the account's mailbox."""

    RESET_PASSWORD = "reset_password"  # noqa: S105 - a purpose name, not a password
    """A link token that lets the person choose a new password."""

    CHANGE_EMAIL = "change_email"
    """A 6-digit code that proves control of a requested new address."""
