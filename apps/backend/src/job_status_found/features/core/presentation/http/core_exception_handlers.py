"""HTTP answers for failures no single feature owns, registered once in `app/app.py`."""

from http import HTTPStatus

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from job_status_found.features.core.presentation.http.problem_details_responses import (
    PROBLEM_JSON_MEDIA_TYPE,
)
from job_status_found.features.core.presentation.http.schemas.invalid_input_error_response import (
    InvalidInputErrorResponse,
)
from job_status_found.features.core.presentation.http.schemas.invalid_input_problem_details_response import (  # noqa: E501
    InvalidInputProblemDetailsResponse,
)

INVALID_INPUT_CODE = "invalid_input"
"""`code` of a request whose body, path, query, or headers fail validation."""


async def handle_request_validation_error(_request: Request, error: Exception) -> JSONResponse:
    """Answer invalid input with a 422 problem that echoes no submitted value.

    FastAPI's default body repeats each invalid input, which can be a whole
    request body with its password.

    Args:
        _request: The rejected request.
        error: The `RequestValidationError` FastAPI raised.

    Returns:
        A 422 `InvalidInputProblemDetailsResponse` response.

    Raises:
        TypeError: The handler was registered for another exception type.
    """
    if not isinstance(error, RequestValidationError):
        error_message = f"Expected RequestValidationError, got {type(error).__name__}."
        raise TypeError(error_message)

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    problem = InvalidInputProblemDetailsResponse(
        title=HTTPStatus(status_code).phrase,
        status=status_code,
        detail="The request has invalid or missing fields.",
        code=INVALID_INPUT_CODE,
        errors=[
            InvalidInputErrorResponse(
                loc=list(validation_error["loc"]),
                msg=validation_error["msg"],
                type=validation_error["type"],
            )
            for validation_error in error.errors()
        ],
    )
    return JSONResponse(problem.model_dump(), status_code, media_type=PROBLEM_JSON_MEDIA_TYPE)
