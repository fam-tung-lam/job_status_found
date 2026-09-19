"""A version 1 email whose identity survives normalization unchanged."""

import unicodedata
from typing import Annotated

from pydantic import BeforeValidator, EmailStr


def _refuse_email_with_compatibility_characters(email: object) -> object:
    """Refuse raw text that NFKC would fold into another mailbox identity.

    This runs before `EmailStr`, because `email-validator` may normalize the
    submitted text and otherwise hide compatibility characters from the check.

    Args:
        email: The raw request field before email parsing and normalization.

    Returns:
        The raw field unchanged.

    Raises:
        ValueError: A string changes under NFKC normalization.
    """
    if isinstance(email, str) and unicodedata.normalize("NFKC", email) != email:
        error_message = "The address contains characters that only look like other characters."
        raise ValueError(error_message)
    return email


type EmailAddressText = Annotated[
    EmailStr, BeforeValidator(_refuse_email_with_compatibility_characters)
]
"""An email parsed only after its raw text passes the NFKC identity check."""
