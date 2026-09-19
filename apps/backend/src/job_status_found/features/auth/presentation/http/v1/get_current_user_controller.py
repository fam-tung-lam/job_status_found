"""`GET /v1/auth/me`: read the signed-in account."""

from typing import Annotated

from fastapi import APIRouter, Depends

from job_status_found.features.auth.application.use_cases.get_current_user_use_case import (
    GetCurrentUserUseCase,
)
from job_status_found.features.auth.di import get_current_user_use_case
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.presentation.http.v1.guards.authentication_guards import (
    get_authenticated_principal,
)
from job_status_found.features.auth.presentation.http.v1.schemas.current_user_response import (
    CurrentUserResponse,
)

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    get_current_user_profile: Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)],
) -> CurrentUserResponse:
    """Return the profile and sign-in methods of the bearer-token account.

    Args:
        principal: The statelessly authenticated access-token principal.
        get_current_user_profile: Reads current account state.

    Returns:
        The fixed current-user JSON contract.
    """
    current_user = await get_current_user_profile.invoke(principal.user_id)
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        avatar_url=current_user.avatar_url,
        locale=current_user.locale,
        role=current_user.role,
        has_password=current_user.has_password,
        linked_providers=current_user.linked_providers,
    )
