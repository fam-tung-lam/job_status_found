"""Input of password sign-in."""

from dataclasses import dataclass, field

from job_status_found.features.auth.application.dtos.session_input import SessionInput


@dataclass(frozen=True, slots=True)
class PasswordSignInInput:
    """The credentials and session choices submitted for password sign-in."""

    email: str
    """The account email."""

    password: str = field(repr=False)
    """The submitted password, excluded from representations."""

    session: SessionInput
    """The client choices and request facts for the new session."""
