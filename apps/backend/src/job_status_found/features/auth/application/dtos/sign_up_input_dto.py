"""Input of an email and password sign-up."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SignUpInputDTO:
    """What a person submits to create an account with email and password."""

    first_name: str
    """Given name, already trimmed and between 1 and 100 characters."""

    last_name: str
    """Family name, already trimmed and between 1 and 100 characters."""

    email: str
    """The address as typed, with its syntax already validated."""

    password: str = field(repr=False)
    """The chosen password in the clear; kept out of `repr` so it never reaches a log."""
