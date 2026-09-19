"""The FastAPI application class whose OpenAPI document describes problem responses."""

from typing import Any, override

from fastapi import FastAPI
from pydantic.json_schema import models_json_schema

from job_status_found.features.core.presentation.http.problem_details_responses import (
    OPENAPI_SCHEMA_REF_TEMPLATE,
    problem_details_openapi_content,
)
from job_status_found.features.core.presentation.http.schemas.invalid_input_problem_details import (
    InvalidInputProblemDetails,
)
from job_status_found.features.core.presentation.http.schemas.problem_details import ProblemDetails


class ProblemDetailsFastAPI(FastAPI):
    """A FastAPI application whose OpenAPI document describes its problem responses.

    It registers the problem schemas and replaces FastAPI's default 422
    description, whose body this app never sends, on every operation.
    """

    @override
    def openapi(self) -> dict[str, Any]:
        """Build the OpenAPI document once, with problem responses, and cache it.

        Returns:
            The OpenAPI document.
        """
        # Reuse the document FastAPI cached on the first call.
        if self.openapi_schema is not None:
            return self.openapi_schema
        document = super().openapi()

        # Register the problem schemas, and drop FastAPI's validation schemas,
        # whose body this app never sends.
        _, definitions = models_json_schema(
            [(ProblemDetails, "serialization"), (InvalidInputProblemDetails, "serialization")],
            ref_template=OPENAPI_SCHEMA_REF_TEMPLATE,
        )
        schemas: dict[str, Any] = document.setdefault("components", {}).setdefault("schemas", {})
        schemas.update(definitions["$defs"])
        schemas.pop("HTTPValidationError", None)
        schemas.pop("ValidationError", None)

        # Describe every operation's 422 as the problem this app sends.
        for path_item in document.get("paths", {}).values():
            for operation in path_item.values():
                if "422" in operation.get("responses", {}):
                    operation["responses"]["422"] = {
                        "description": "`invalid_input`: a field is missing or malformed.",
                        "content": problem_details_openapi_content(InvalidInputProblemDetails),
                    }
        return document
