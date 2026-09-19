"""FastAPI dependencies that authenticate version 1 requests and require roles."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from job_status_found.features.auth.application.use_cases.authenticate_access_token_use_case import (  # noqa: E501
    AuthenticateAccessTokenUseCase,
)
from job_status_found.features.auth.application.use_cases.require_user_role_use_case import (
    RequireUserRoleUseCase,
)
from job_status_found.features.auth.di import (
    get_authenticate_access_token_use_case,
    get_require_user_role_use_case,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.failures.access_token_authentication_failure import (
    AccessTokenAuthenticationFailure,
)
from job_status_found.features.auth.domain.failures.required_user_role_not_granted_failure import (
    RequiredUserRoleNotGrantedFailure,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole

_optional_bearer = HTTPBearer(auto_error=False)
"""Bearer parser whose missing-credential result is mapped by our problem handler."""


async def get_optional_authenticated_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_optional_bearer)],
    authenticate_access_token: Annotated[
        AuthenticateAccessTokenUseCase, Depends(get_authenticate_access_token_use_case)
    ],
) -> AuthenticatedPrincipal | None:
    """Authenticate an optional bearer token.

    Args:
        credentials: The parsed bearer header, when present.
        authenticate_access_token: Verifies the token without reading a table.

    Returns:
        The authenticated principal, or `None` when no bearer header was sent.
    """
    if credentials is None:
        return None
    return authenticate_access_token.invoke(credentials.credentials)


async def get_authenticated_principal(
    principal: Annotated[
        AuthenticatedPrincipal | None, Depends(get_optional_authenticated_principal)
    ],
) -> AuthenticatedPrincipal:
    """Require and return one authenticated principal.

    Args:
        principal: The optionally authenticated bearer principal.

    Returns:
        The authenticated principal.

    Raises:
        AccessTokenAuthenticationFailure: No bearer credential was sent.
    """
    if principal is None:
        raise AccessTokenAuthenticationFailure
    return principal


async def get_lenient_optional_authenticated_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_optional_bearer)],
    authenticate_access_token: Annotated[
        AuthenticateAccessTokenUseCase, Depends(get_authenticate_access_token_use_case)
    ],
) -> AuthenticatedPrincipal | None:
    """Authenticate a bearer token when possible and otherwise return no principal.

    Sign-out uses this dependency because its contract is deliberately
    idempotent and promises no credential failure.

    Args:
        credentials: The parsed bearer header, when present.
        authenticate_access_token: Verifies the token without reading a table.

    Returns:
        The authenticated principal, or `None` for a missing or invalid token.
    """
    if credentials is None:
        return None
    try:
        return authenticate_access_token.invoke(credentials.credentials)
    except AccessTokenAuthenticationFailure:
        return None


def require_role(required_role: UserRole) -> Callable[..., Awaitable[AuthenticatedPrincipal]]:
    """Build a dependency that requires an account's current stored role.

    Args:
        required_role: The role the protected operation needs.

    Returns:
        A dependency that returns the principal after the stored-role check.
    """

    async def require_stored_role(
        principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
        require_user_role: Annotated[
            RequireUserRoleUseCase, Depends(get_require_user_role_use_case)
        ],
    ) -> AuthenticatedPrincipal:
        """Require the configured role from current database state.

        Args:
            principal: The access-token principal.
            require_user_role: Loads and checks the stored role.

        Returns:
            The principal after authorization.

        Raises:
            HTTPException: The stored role does not grant the operation.
        """
        try:
            await require_user_role.invoke(principal.user_id, required_role)
        except RequiredUserRoleNotGrantedFailure as error:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "The role is not allowed.") from error
        return principal

    return require_stored_role
