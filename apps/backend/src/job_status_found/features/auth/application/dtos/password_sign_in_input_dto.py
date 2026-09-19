"""Input of password sign-in."""

from dataclasses import dataclass, field

from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO


@dataclass(frozen=True, slots=True)
class PasswordSignInInputDTO:
    """The credentials and session choices submitted for password sign-in."""

    email: str
    """The account email."""

    password: str = field(repr=False)
    """The submitted password, excluded from representations."""

    session: SessionInputDTO
    """The client choices and request facts for the new session."""
