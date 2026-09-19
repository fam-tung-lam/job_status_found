"""Input of confirming an emailed verification code."""

from dataclasses import dataclass, field

from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO


@dataclass(frozen=True, slots=True)
class ConfirmEmailVerificationInputDTO:
    """The mailbox, code, password, and session choices submitted together."""

    email: str
    """The mailbox being proved."""

    code: str = field(repr=False)
    """The six-digit code from the email."""

    password: str = field(repr=False)
    """The password whose account version the code confirms."""

    session: SessionInputDTO
    """The client choices and request facts for the new session."""
