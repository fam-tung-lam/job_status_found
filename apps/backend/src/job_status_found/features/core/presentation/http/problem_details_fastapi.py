"""The FastAPI application class whose OpenAPI document describes problem responses."""

from typing import Any, override

from fastapi import FastAPI
from pydantic.json_schema import models_json_schema

from job_status_found.features.core.presentation.http.problem_details_responses import (
    SCHEMA_REF_TEMPLATE,
    problem_details_content,
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
        if self.openapi_schema is not None:
            return self.openapi_schema
        document = super().openapi()
        _, definitions = models_json_schema(
            [(ProblemDetails, "serialization"), (InvalidInputProblemDetails, "serialization")],
            ref_template=SCHEMA_REF_TEMPLATE,
        )
        schemas: dict[str, Any] = document.setdefault("components", {}).setdefault("schemas", {})
        schemas.update(definitions["$defs"])
        schemas.pop("HTTPValidationError", None)
        schemas.pop("ValidationError", None)
        for path_item in document.get("paths", {}).values():
            for operation in path_item.values():
                if "422" in operation.get("responses", {}):
                    operation["responses"]["422"] = {
                        "description": "`invalid_input`: a field is missing or malformed.",
                        "content": problem_details_content(InvalidInputProblemDetails),
                    }
        return document
