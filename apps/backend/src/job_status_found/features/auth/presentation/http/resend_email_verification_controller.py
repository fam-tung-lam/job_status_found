"""`POST /v1/auth/email-verification/resend`: invisibly resend a code."""

from datetime import timedelta
from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, Response, status

from job_status_found.features.auth.application.use_cases.resend_email_verification_use_case import (  # noqa: E501
    ResendEmailVerificationUseCase,
)
from job_status_found.features.auth.di import (
    get_resend_email_verification_use_case,
    get_sign_up_min_response_time,
)
from job_status_found.features.auth.presentation.http.schemas.resend_email_verification_request import (  # noqa: E501
    ResendEmailVerificationRequest,
)

router = APIRouter()


@router.post(
    "/email-verification/resend",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def resend_email_verification(
    resend_request: ResendEmailVerificationRequest,
    resend_verification: Annotated[
        ResendEmailVerificationUseCase, Depends(get_resend_email_verification_use_case)
    ],
    min_response_time: Annotated[timedelta, Depends(get_sign_up_min_response_time)],
) -> Response:
    """Queue a replacement code without revealing account state by body or timing.

    Args:
        resend_request: The syntactically validated mailbox.
        resend_verification: The paced resend operation.
        min_response_time: The same enumeration floor as sign-up.

    Returns:
        The identical empty 202 response for every account state.
    """
    earliest_response_at = anyio.current_time() + min_response_time.total_seconds()
    await resend_verification.invoke(resend_request.email)
    await anyio.sleep_until(earliest_response_at)
    return Response(status_code=status.HTTP_202_ACCEPTED)
