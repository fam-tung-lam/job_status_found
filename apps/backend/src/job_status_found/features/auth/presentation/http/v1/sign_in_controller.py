"""`POST /v1/auth/sign-in`: open a password session."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from job_status_found.features.auth.application.dtos.password_sign_in_input_dto import (
    PasswordSignInInputDTO,
)
from job_status_found.features.auth.application.use_cases.sign_in_with_password_use_case import (
    SignInWithPasswordUseCase,
)
from job_status_found.features.auth.di import (
    get_refresh_cookie_settings,
    get_sign_in_with_password_use_case,
)
from job_status_found.features.auth.presentation.http.v1.helpers.build_session_input_from_request import (  # noqa: E501
    build_session_input_from_request,
)
from job_status_found.features.auth.presentation.http.v1.helpers.deliver_token_pair_to_client import (  # noqa: E501
    deliver_token_pair_to_client,
)
from job_status_found.features.auth.presentation.http.v1.refresh_cookie_settings import (
    RefreshCookieSettings,
)
from job_status_found.features.auth.presentation.http.v1.schemas.password_sign_in_request import (
    PasswordSignInRequest,
)
from job_status_found.features.auth.presentation.http.v1.schemas.token_pair_response import (
    TokenPairResponse,
)

router = APIRouter()


@router.post("/sign-in", response_model=TokenPairResponse, response_model_exclude_none=True)
async def sign_in(
    sign_in_request: PasswordSignInRequest,
    request: Request,
    response: Response,
    sign_in_with_password: Annotated[
        SignInWithPasswordUseCase, Depends(get_sign_in_with_password_use_case)
    ],
    cookie_settings: Annotated[RefreshCookieSettings, Depends(get_refresh_cookie_settings)],
) -> TokenPairResponse:
    """Verify a password and deliver a new session through its fixed client channel.

    Args:
        sign_in_request: The credentials and session choices.
        request: The inbound request, which supplies safe session metadata.
        response: The response whose web refresh cookie may be set.
        sign_in_with_password: The password sign-in operation.
        cookie_settings: The web refresh-cookie contract.

    Returns:
        The access token and, for mobile only, refresh token.
    """
    token_pair = await sign_in_with_password.invoke(
        PasswordSignInInputDTO(
            email=sign_in_request.email,
            password=sign_in_request.password,
            session=build_session_input_from_request(
                request,
                sign_in_request.client_kind,
                remember_me=sign_in_request.remember_me,
            ),
        )
    )
    return deliver_token_pair_to_client(response, token_pair, cookie_settings)
