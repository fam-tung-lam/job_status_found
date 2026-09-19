"""Request body of the email and password sign-up."""

import unicodedata
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, StringConstraints

type PersonName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]*$"
    ),
]
"""A given or family name: trimmed, 1 to 100 characters, without control characters."""


def _refuse_email_with_compatibility_characters(email: str) -> str:
    """Refuse an address that NFKC normalization would change, such as one with full-width letters.

    Normalization folds such characters into their plain form, so the address
    would share an account with a different mailbox.

    Args:
        email: The address after `EmailStr` validation.

    Returns:
        The address, unchanged.

    Raises:
        ValueError: The address contains compatibility characters.
    """
    if unicodedata.normalize("NFKC", email) != email:
        error_message = "The address contains characters that only look like other characters."
        raise ValueError(error_message)
    return email


def _refuse_password_not_encodable_as_utf8(password: str) -> str:
    """Refuse a password that cannot be encoded as UTF-8, such as one with a lone surrogate.

    JSON can carry a lone surrogate, which no hash can encode, so it would
    otherwise fail later as a 500.

    Args:
        password: The submitted password.

    Returns:
        The password, unchanged.

    Raises:
        ValueError: The password contains a lone surrogate.
    """
    try:
        password.encode()
    except UnicodeEncodeError as error:
        error_message = "The password contains an invalid Unicode character."
        raise ValueError(error_message) from error
    return password


class SignUpRequest(BaseModel):
    """What the sign-up page submits; the backend stamps the terms version itself."""

    model_config = ConfigDict(
        frozen=True,
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "jane.doe@example.com",
                    "password": "correct horse battery staple",
                }
            ]
        },
    )

    first_name: PersonName
    """Given name."""

    last_name: PersonName
    """Family name."""

    email: Annotated[EmailStr, AfterValidator(_refuse_email_with_compatibility_characters)]
    """The address to verify, as `email-validator` normalizes it: the domain lower-cased.

    Its syntax is checked, its mailbox is not. An address with compatibility
    characters, such as full-width letters, is refused.
    """

    password: Annotated[str, AfterValidator(_refuse_password_not_encodable_as_utf8)]
    """The chosen password; 12 to 128 Unicode code points unless the minimum is configured."""
