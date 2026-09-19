"""`POST /v1/auth/sign-out`: revoke one session and clear its web cookie."""

import re
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response, status

from job_status_found.features.auth.application.use_cases.sign_out_use_case import SignOutUseCase
from job_status_found.features.auth.auth_settings import AuthSettings, get_auth_settings
from job_status_found.features.auth.di import get_refresh_cookie_settings, get_sign_out_use_case
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.failures.session_refresh_failure import (
    SessionRefreshOriginNotAllowed,
)
from job_status_found.features.auth.presentation.http.guards.authentication_guards import (
    get_lenient_optional_authenticated_principal,
)
from job_status_found.features.auth.presentation.http.helpers.clear_refresh_cookie import (
    clear_refresh_cookie,
)
from job_status_found.features.auth.presentation.http.refresh_cookie_settings import (
    RefreshCookieSettings,
)
from job_status_found.features.auth.presentation.http.schemas.refresh_session_request import (
    RefreshSessionRequest,
)
from job_status_found.features.core import AppSettings, get_app_settings

router = APIRouter()


@router.post("/sign-out", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def sign_out(
    request: Request,
    response: Response,
    sign_out_use_case: Annotated[SignOutUseCase, Depends(get_sign_out_use_case)],
    principal: Annotated[
        AuthenticatedPrincipal | None,
        Depends(get_lenient_optional_authenticated_principal),
    ],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    app_settings: Annotated[AppSettings, Depends(get_app_settings)],
    cookie_settings: Annotated[RefreshCookieSettings, Depends(get_refresh_cookie_settings)],
    refresh_request: Annotated[RefreshSessionRequest | None, Body()] = None,
) -> Response:
    """End the cookie, body-token, or bearer session idempotently.

    Args:
        request: The inbound cookie and Origin header.
        response: The response whose cookie is cleared.
        sign_out_use_case: Revokes the addressed session.
        principal: The optional bearer credential, lowest precedence.
        auth_settings: Names the refresh cookie.
        app_settings: Provides the allowed browser origins.
        cookie_settings: Supplies the exact cookie deletion attributes.
        refresh_request: The optional mobile refresh-token body.

    Returns:
        The empty 204 response.

    Raises:
        SessionRefreshOriginNotAllowed: A cookie request lacks an allowed Origin.
    """
    cookie_token = request.cookies.get(auth_settings.refresh_cookie_name)
    if cookie_token is not None:
        origin = request.headers.get("origin")
        if origin is None or re.fullmatch(app_settings.cors_allow_origin_regex, origin) is None:
            raise SessionRefreshOriginNotAllowed
    body_token = refresh_request.refresh_token if refresh_request is not None else None
    await sign_out_use_case.invoke(
        refresh_token=cookie_token or body_token,
        principal=principal,
    )
    clear_refresh_cookie(response, cookie_settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
