"""Authentication feature facade for identities, sessions, and authorization guards."""

from job_status_found.features.auth.application.use_cases.authenticate_access_token_use_case import (  # noqa: E501
    AuthenticateAccessTokenUseCase,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.auth.presentation.http.v1.guards.authentication_guards import (
    get_authenticated_principal,
    require_role,
)

__all__ = [
    "AuthenticateAccessTokenUseCase",
    "AuthenticatedPrincipal",
    "UserRole",
    "get_authenticated_principal",
    "require_role",
]
