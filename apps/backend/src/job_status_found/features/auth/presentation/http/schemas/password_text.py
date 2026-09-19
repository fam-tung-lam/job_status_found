"""A password string that every Argon2id operation can encode."""

from typing import Annotated

from pydantic import AfterValidator


def _refuse_password_not_encodable_as_utf8(password: str) -> str:
    """Refuse a password containing a lone Unicode surrogate.

    Args:
        password: The submitted password.

    Returns:
        The password unchanged when UTF-8 can encode it.

    Raises:
        ValueError: The password contains a lone surrogate.
    """
    try:
        password.encode()
    except UnicodeEncodeError as error:
        error_message = "The password contains an invalid Unicode character."
        raise ValueError(error_message) from error
    return password


type PasswordText = Annotated[str, AfterValidator(_refuse_password_not_encodable_as_utf8)]
"""A password accepted by the UTF-8-based hashing library."""
