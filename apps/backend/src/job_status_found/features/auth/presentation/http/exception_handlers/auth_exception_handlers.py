"""HTTP answers for auth failures, registered once in `app/app.py`."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from job_status_found.features.auth.domain.failures.password_sign_in_failure import (
    PasswordSignInAccountUnavailable,
    PasswordSignInEmailNotVerified,
    PasswordSignInInvalidCredentials,
)
from job_status_found.features.auth.domain.failures.session_refresh_failure import (
    SessionRefreshOriginNotAllowed,
    SessionRefreshSessionEnded,
    SessionRefreshTokenInvalid,
)
from job_status_found.features.auth.domain.failures.sign_up_failure import (
    SignUpFailure,
    SignUpPasswordTooWeak,
)
from job_status_found.features.core import problem_details_response

PASSWORD_TOO_WEAK_CODE = "password_too_weak"  # noqa: S105 - a failure code, not a password
"""`code` of a new password outside the password policy."""

_BEARER_HEADERS = {"WWW-Authenticate": "Bearer"}
"""Challenge header required on every bearer-related 401 response."""


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
            error_message = (
                f"No HTTP answer for {type(failure).__name__}; is it a {SignUpFailure.__name__}?"
            )
            raise TypeError(error_message)


async def handle_email_verification_failure(_request: Request, failure: Exception) -> JSONResponse:
    """Answer any refused email proof with the same problem.

    Args:
        _request: The refused request.
        failure: The verification failure.

    Returns:
        The generic verification-code problem.
    """
    return problem_details_response(
        status.HTTP_400_BAD_REQUEST, "verification_code_invalid", str(failure)
    )


async def handle_access_token_authentication_failure(
    _request: Request, failure: Exception
) -> JSONResponse:
    """Answer an invalid bearer access token.

    Args:
        _request: The refused request.
        failure: The bearer authentication failure.

    Returns:
        The generic bearer problem and challenge header.
    """
    response = problem_details_response(
        status.HTTP_401_UNAUTHORIZED, "access_token_invalid", str(failure)
    )
    response.headers.update(_BEARER_HEADERS)
    return response


async def handle_password_sign_in_failure(_request: Request, failure: Exception) -> JSONResponse:
    """Answer a refused password sign-in with its stable problem code.

    Args:
        _request: The refused request.
        failure: The sign-in failure variant.

    Returns:
        The mapped sign-in problem.

    Raises:
        TypeError: The variant is unknown.
    """
    match failure:
        case PasswordSignInInvalidCredentials():
            response = problem_details_response(
                status.HTTP_401_UNAUTHORIZED, "invalid_credentials", str(failure)
            )
            response.headers.update(_BEARER_HEADERS)
            return response
        case PasswordSignInEmailNotVerified():
            return problem_details_response(
                status.HTTP_403_FORBIDDEN, "email_verification_required", str(failure)
            )
        case PasswordSignInAccountUnavailable():
            return problem_details_response(
                status.HTTP_403_FORBIDDEN, "account_unavailable", str(failure)
            )
        case _:
            raise TypeError(f"No HTTP answer for {type(failure).__name__}.")


async def handle_session_refresh_failure(_request: Request, failure: Exception) -> JSONResponse:
    """Answer a refused refresh or cookie-origin check.

    Args:
        _request: The refused request.
        failure: The refresh failure variant.

    Returns:
        The mapped refresh problem.

    Raises:
        TypeError: The variant is unknown.
    """
    match failure:
        case SessionRefreshTokenInvalid():
            response = problem_details_response(
                status.HTTP_401_UNAUTHORIZED, "refresh_token_invalid", str(failure)
            )
            response.headers.update(_BEARER_HEADERS)
            return response
        case SessionRefreshSessionEnded():
            response = problem_details_response(
                status.HTTP_401_UNAUTHORIZED, "session_ended", str(failure)
            )
            response.headers.update(_BEARER_HEADERS)
            return response
        case SessionRefreshOriginNotAllowed():
            return problem_details_response(
                status.HTTP_403_FORBIDDEN, "origin_not_allowed", str(failure)
            )
        case _:
            raise TypeError(f"No HTTP answer for {type(failure).__name__}.")
