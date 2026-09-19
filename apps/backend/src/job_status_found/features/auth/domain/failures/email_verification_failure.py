"""Failures of confirming an emailed verification code."""


class EmailVerificationFailure(Exception):
    """A verification request could not prove its mailbox and password together."""


class EmailVerificationCodeInvalidFailure(EmailVerificationFailure):
    """The submitted proof is invalid, expired, consumed, or exhausted."""

    def __init__(self) -> None:
        """Describe the deliberately non-specific verification failure."""
        super().__init__("The verification code is invalid or has expired.")
