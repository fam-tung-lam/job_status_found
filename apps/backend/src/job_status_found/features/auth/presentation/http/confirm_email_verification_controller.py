"""`POST /v1/auth/email-verification/confirm`: verify and open a session."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from job_status_found.features.auth.application.dtos.confirm_email_verification_input import (
    ConfirmEmailVerificationInput,
)
from job_status_found.features.auth.application.use_cases.confirm_email_verification_use_case import (  # noqa: E501
    ConfirmEmailVerificationUseCase,
)
from job_status_found.features.auth.di import (
    get_confirm_email_verification_use_case,
    get_refresh_cookie_settings,
)
from job_status_found.features.auth.presentation.http.helpers.build_session_input_from_request import (  # noqa: E501
    build_session_input_from_request,
)
from job_status_found.features.auth.presentation.http.helpers.deliver_token_pair_to_client import (
    deliver_token_pair_to_client,
)
from job_status_found.features.auth.presentation.http.refresh_cookie_settings import (
    RefreshCookieSettings,
)
from job_status_found.features.auth.presentation.http.schemas.confirm_email_verification_request import (  # noqa: E501
    ConfirmEmailVerificationRequest,
)
from job_status_found.features.auth.presentation.http.schemas.token_pair_response import (
    TokenPairResponse,
)

router = APIRouter()


@router.post(
    "/email-verification/confirm",
    response_model=TokenPairResponse,
    response_model_exclude_none=True,
)
async def confirm_email_verification(
    confirmation_request: ConfirmEmailVerificationRequest,
    request: Request,
    response: Response,
    confirm_email_verification: Annotated[
        ConfirmEmailVerificationUseCase, Depends(get_confirm_email_verification_use_case)
    ],
    cookie_settings: Annotated[RefreshCookieSettings, Depends(get_refresh_cookie_settings)],
) -> TokenPairResponse:
    """Verify the jointly submitted code and password, then open a session.

    Args:
        confirmation_request: The mailbox proof and session choices.
        request: The inbound request, which supplies safe session metadata.
        response: The response whose web refresh cookie may be set.
        confirm_email_verification: The confirmation operation.
        cookie_settings: The web refresh-cookie contract.

    Returns:
        The access token and, for mobile only, refresh token.
    """
    token_pair = await confirm_email_verification.invoke(
        ConfirmEmailVerificationInput(
            email=confirmation_request.email,
            code=confirmation_request.code,
            password=confirmation_request.password,
            session=build_session_input_from_request(
                request,
                confirmation_request.client_kind,
                remember_me=confirmation_request.remember_me,
            ),
        )
    )
    return deliver_token_pair_to_client(response, token_pair, cookie_settings)
