"""Response body of reading the signed-in account."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from job_status_found.features.auth.domain.value_objects.identity_provider import IdentityProvider
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class CurrentUserResponse(BaseModel):
    """The profile and sign-in methods of the authenticated account."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    id: UUID
    """The account id."""

    email: str
    """The verified email address."""

    first_name: str | None
    """The given name, when known."""

    last_name: str | None
    """The family name, when known."""

    avatar_url: str | None
    """The provider picture URL, when one exists."""

    locale: str | None
    """The preferred BCP 47 locale, when known."""

    role: UserRole
    """The account's current role."""

    has_password: bool
    """Whether password sign-in is available."""

    linked_providers: tuple[IdentityProvider, ...]
    """The external providers linked to the account."""
