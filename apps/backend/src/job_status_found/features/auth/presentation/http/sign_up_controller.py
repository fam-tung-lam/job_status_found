"""`POST /v1/auth/sign-up`: create an account with email and password."""

from datetime import timedelta
from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, Response, status

from job_status_found.features.auth.application.dtos.sign_up_input import SignUpInput
from job_status_found.features.auth.application.use_cases.sign_up_with_password_use_case import (
    SignUpWithPasswordUseCase,
)
from job_status_found.features.auth.di import (
    get_sign_up_min_response_time,
    get_sign_up_with_password_use_case,
)
from job_status_found.features.auth.presentation.http.schemas.sign_up_request import (
    SignUpRequest,
)
from job_status_found.features.core import problem_details_content

router = APIRouter()


@router.post(
    "/sign-up",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
    # Set explicitly, so the docstring's `Args:` section stays out of the public docs.
    description="Create an account with email and password, or email the owner of an existing "
    "one. The answer is the same for every email and comes no sooner than a fixed minimum "
    "response time, so it never reveals which emails have accounts.",
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "Accepted with an empty body, whether or not the email has an "
            "account. A new or unverified email receives a verification code; a verified "
            "one receives a notice."
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "`password_too_weak`: the password is shorter than the configured "
            "minimum (12 by default) or longer than 128 characters.",
            "content": problem_details_content(),
        },
    },
)
async def sign_up(
    body: SignUpRequest,
    sign_up_with_password: Annotated[
        SignUpWithPasswordUseCase, Depends(get_sign_up_with_password_use_case)
    ],
    min_response_time: Annotated[timedelta, Depends(get_sign_up_min_response_time)],
) -> Response:
    """Create an account with email and password, or email the owner of an existing one.

    The answer is the same for every email and comes no sooner than the
    configured minimum response time, so neither its body nor its timing
    reveals which emails have accounts. The email goes out after the response.

    Args:
        body: The submitted names, email, and password.
        sign_up_with_password: The sign-up use case.
        min_response_time: The shortest time an accepted sign-up takes to answer.

    Returns:
        An empty 202 response.
    """
    answer_at = anyio.current_time() + min_response_time.total_seconds()
    await sign_up_with_password.invoke(
        SignUpInput(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            password=body.password,
        )
    )
    await anyio.sleep_until(answer_at)
    return Response(status_code=status.HTTP_202_ACCEPTED)
