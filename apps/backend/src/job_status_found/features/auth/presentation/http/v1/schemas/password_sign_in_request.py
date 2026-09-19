"""Version 1 request body of password sign-in."""

from pydantic import BaseModel, ConfigDict

from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.presentation.http.v1.schemas.email_address_text import (
    EmailAddressText,
)
from job_status_found.features.auth.presentation.http.v1.schemas.password_text import PasswordText


class PasswordSignInRequest(BaseModel):
    """The password credentials and session choices."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    email: EmailAddressText
    """The account email."""

    password: PasswordText
    """The submitted password; no new-password policy is applied here."""

    client_kind: ClientKind
    """The client platform and refresh-token channel."""

    remember_me: bool
    """Whether the new session remembers the device."""
