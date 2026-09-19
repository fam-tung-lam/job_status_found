"""Problem responses and their OpenAPI description, for every feature's endpoints."""

from http import HTTPStatus
from typing import Any

from fastapi.responses import JSONResponse

from job_status_found.features.core.presentation.http.schemas.problem_details import ProblemDetails

PROBLEM_JSON_MEDIA_TYPE = "application/problem+json"
"""Media type of every error response."""

SCHEMA_REF_TEMPLATE = "#/components/schemas/{model}"
"""Where OpenAPI keeps a named schema."""


def problem_details_response(
    status_code: int, code: str, detail: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    """Build an `application/problem+json` response.

    Args:
        status_code: The HTTP status.
        code: The stable failure code.
        detail: Human-readable explanation.
        headers: Extra response headers, such as `WWW-Authenticate`.

    Returns:
        The response carrying a `ProblemDetails` body.
    """
    problem = ProblemDetails(
        title=HTTPStatus(status_code).phrase, status=status_code, detail=detail, code=code
    )
    return JSONResponse(
        problem.model_dump(), status_code, headers=headers, media_type=PROBLEM_JSON_MEDIA_TYPE
    )


def problem_details_content(model: type[ProblemDetails] = ProblemDetails) -> dict[str, Any]:
    """Describe a problem body for a route's `responses=` entry.

    FastAPI files a response `model` under the route's own media type, which is
    `application/json`, so a problem body names its schema here instead.
    `ProblemDetailsFastAPI` registers the schema it points to.

    Args:
        model: The problem model the response carries.

    Returns:
        The `content` value of an OpenAPI response object.
    """
    ref = SCHEMA_REF_TEMPLATE.format(model=model.__name__)
    return {PROBLEM_JSON_MEDIA_TYPE: {"schema": {"$ref": ref}}}
