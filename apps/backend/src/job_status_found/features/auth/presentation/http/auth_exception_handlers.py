"""HTTP answers for auth failures, registered once in `app/app.py`."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from job_status_found.features.auth.domain.failures.sign_up_failure import (
    SignUpFailure,
    SignUpPasswordTooWeak,
)
from job_status_found.features.core import problem_details_response

PASSWORD_TOO_WEAK_CODE = "password_too_weak"  # noqa: S105 - a failure code, not a password
"""`code` of a new password outside the password policy."""


async def handle_sign_up_failure(_request: Request, failure: Exception) -> JSONResponse:
    """Answer a refused sign-up with its problem response.

    Args:
        _request: The refused request.
        failure: The `SignUpFailure` the use case raised.

    Returns:
        The problem response for the failure's cause.

    Raises:
        TypeError: The failure is not a known `SignUpFailure` variant.
    """
    match failure:
        case SignUpPasswordTooWeak():
            return problem_details_response(
                status.HTTP_400_BAD_REQUEST, PASSWORD_TOO_WEAK_CODE, str(failure)
            )
        case _:
            msg = f"No HTTP answer for {type(failure).__name__}; is it a {SignUpFailure.__name__}?"
            raise TypeError(msg)
