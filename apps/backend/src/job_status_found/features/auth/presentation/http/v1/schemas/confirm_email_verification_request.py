"""Version 1 request body of email verification confirmation."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.presentation.http.v1.schemas.email_address_text import (
    EmailAddressText,
)
from job_status_found.features.auth.presentation.http.v1.schemas.password_text import PasswordText


class ConfirmEmailVerificationRequest(BaseModel):
    """The code, password, and session choices submitted together."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    email: EmailAddressText
    """The mailbox being proved."""

    code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")]
    """The six-digit code from the email."""

    password: PasswordText
    """The password whose account version the code confirms."""

    client_kind: ClientKind
    """The client platform and refresh-token channel."""

    remember_me: bool
    """Whether the new session remembers the device."""
