"""The account details one sign-up writes."""

from dataclasses import dataclass
from datetime import datetime

from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress


@dataclass(frozen=True, slots=True)
class UserRegistrationDTO:
    """The details of an unverified account, from its latest sign-up."""

    email: EmailAddress
    """The address the account is reached at."""

    first_name: str
    """Given name."""

    last_name: str
    """Family name."""

    registered_at: datetime
    """When the person signed up."""
