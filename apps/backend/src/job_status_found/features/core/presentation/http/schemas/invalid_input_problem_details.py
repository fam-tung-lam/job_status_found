"""The body of a 422 response."""

from pydantic import ConfigDict

from job_status_found.features.core.presentation.http.schemas.invalid_input_error import (
    InvalidInputError,
)
from job_status_found.features.core.presentation.http.schemas.problem_details import ProblemDetails


class InvalidInputProblemDetails(ProblemDetails):
    """A 422 problem that also lists each invalid field."""

    model_config = ConfigDict(
        frozen=True,
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [
                {
                    "type": "about:blank",
                    "title": "Unprocessable Content",
                    "status": 422,
                    "detail": "The request has invalid or missing fields.",
                    "code": "invalid_input",
                    "errors": [
                        {
                            "loc": ["body", "email"],
                            "msg": "value is not a valid email address",
                            "type": "value_error",
                        }
                    ],
                }
            ]
        },
    )

    errors: list[InvalidInputError]
    """Every field that failed validation."""
