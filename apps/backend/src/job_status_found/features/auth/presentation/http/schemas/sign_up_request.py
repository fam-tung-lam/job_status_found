"""Request body of the email and password sign-up."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from job_status_found.features.auth.presentation.http.schemas.email_address_text import (
    EmailAddressText,
)
from job_status_found.features.auth.presentation.http.schemas.password_text import PasswordText

type PersonName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]*$"
    ),
]
"""A given or family name: trimmed, 1 to 100 characters, without control characters."""


class SignUpRequest(BaseModel):
    """What the sign-up page submits to create an account with email and password."""

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

    email: EmailAddressText
    """The address to verify, as `email-validator` normalizes it: the domain lower-cased.

    Its syntax is checked, its mailbox is not. An address with compatibility
    characters, such as full-width letters, is refused.
    """

    password: PasswordText
    """The chosen password; 12 to 128 Unicode code points unless the minimum is configured."""
