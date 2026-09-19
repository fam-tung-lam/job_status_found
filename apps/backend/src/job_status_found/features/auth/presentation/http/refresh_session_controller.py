"""`POST /v1/auth/token/refresh`: rotate a session credential."""

import re
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, Response

from job_status_found.features.auth.application.use_cases.refresh_session_use_case import (
    RefreshSessionUseCase,
)
from job_status_found.features.auth.auth_settings import AuthSettings, get_auth_settings
from job_status_found.features.auth.di import (
    get_refresh_cookie_settings,
    get_refresh_session_use_case,
)
from job_status_found.features.auth.domain.failures.session_refresh_failure import (
    SessionRefreshTokenInvalid,
)
from job_status_found.features.auth.presentation.http.helpers.deliver_token_pair_to_client import (
    deliver_token_pair_to_client,
)
from job_status_found.features.auth.presentation.http.refresh_cookie_settings import (
    RefreshCookieSettings,
)
from job_status_found.features.auth.presentation.http.schemas.refresh_session_request import (
    RefreshSessionRequest,
)
from job_status_found.features.auth.presentation.http.schemas.token_pair_response import (
    TokenPairResponse,
)
from job_status_found.features.core import AppSettings, get_app_settings

router = APIRouter()


@router.post("/token/refresh", response_model=TokenPairResponse, response_model_exclude_none=True)
async def refresh_session(
    request: Request,
    response: Response,
    refresh_session_use_case: Annotated[
        RefreshSessionUseCase, Depends(get_refresh_session_use_case)
    ],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    app_settings: Annotated[AppSettings, Depends(get_app_settings)],
    cookie_settings: Annotated[RefreshCookieSettings, Depends(get_refresh_cookie_settings)],
    refresh_request: Annotated[RefreshSessionRequest | None, Body()] = None,
) -> TokenPairResponse:
    """Rotate a cookie or body refresh token through its stored client channel.

    Args:
        request: The inbound request with the cookie and Origin header.
        response: The response whose web cookie may rotate.
        refresh_session_use_case: Performs serialized rotation and replay detection.
        auth_settings: Names the configured cookie.
        app_settings: Provides the CORS origin allow-list.
        cookie_settings: The exact cookie delivery attributes.
        refresh_request: The optional mobile body credential.

    Returns:
        The replacement credentials through the stored session channel.

    Raises:
        SessionRefreshTokenInvalid: Neither channel supplied a credential.
    """
    cookie_token = request.cookies.get(auth_settings.refresh_cookie_name)
    refresh_token = cookie_token or (
        refresh_request.refresh_token if refresh_request is not None else None
    )
    if refresh_token is None:
        raise SessionRefreshTokenInvalid
    origin = request.headers.get("origin")
    is_origin_allowed = (
        origin is not None
        and re.fullmatch(app_settings.cors_allow_origin_regex, origin) is not None
    )
    token_pair = await refresh_session_use_case.invoke(
        refresh_token, is_origin_allowed=is_origin_allowed
    )
    return deliver_token_pair_to_client(response, token_pair, cookie_settings)
