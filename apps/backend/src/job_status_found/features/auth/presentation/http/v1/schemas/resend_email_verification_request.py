"""Version 1 request body of verification-code resend."""

from pydantic import BaseModel, ConfigDict

from job_status_found.features.auth.presentation.http.v1.schemas.email_address_text import (
    EmailAddressText,
)


class ResendEmailVerificationRequest(BaseModel):
    """The mailbox that may receive a replacement verification code."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    email: EmailAddressText
    """The syntactically validated mailbox."""
