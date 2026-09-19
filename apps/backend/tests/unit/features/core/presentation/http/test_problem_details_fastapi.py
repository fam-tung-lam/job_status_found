"""Unit tests of the OpenAPI document `ProblemDetailsFastAPI` builds."""

from fastapi import status
from pydantic import BaseModel

from job_status_found.features.core import ProblemDetailsFastAPI, problem_details_openapi_content


class _BodyWithRequiredName(BaseModel):
    """A request body, so the route can fail validation with a 422."""

    name: str
    """A required field, so a body without it is invalid."""


class TestProblemDetailsFastAPI:
    """How the OpenAPI document of `ProblemDetailsFastAPI` describes errors."""

    def test_the_openapi_document_describes_errors_as_problem_json(self) -> None:
        """
        Given: an app with a route that takes a body and documents a 400 problem.
        When: the OpenAPI document is built.
        Then: the 400 and the 422 each name their problem schema as problem+json.
        And: FastAPI's default validation error schema is gone.
        """
        # Given: an app with a route that takes a body and promises a 400 problem.
        app = ProblemDetailsFastAPI()

        @app.post(
            "/things",
            responses={
                status.HTTP_400_BAD_REQUEST: {
                    "description": "x",
                    "content": problem_details_openapi_content(),
                }
            },
        )
        async def create_thing(body: _BodyWithRequiredName) -> None:
            """Accept a thing; only the route's OpenAPI description matters here."""

        # When: the OpenAPI document is built.
        document = app.openapi()

        # Then: both errors name their schema under the media type the app sends,
        # and FastAPI's default validation body, which the app never sends, is gone.
        responses = document["paths"]["/things"]["post"]["responses"]
        assert responses["400"]["content"] == {
            "application/problem+json": {
                "schema": {"$ref": "#/components/schemas/ProblemDetailsResponse"}
            }
        }
        assert responses["422"]["content"] == {
            "application/problem+json": {
                "schema": {"$ref": "#/components/schemas/InvalidInputProblemDetailsResponse"}
            }
        }
        schemas = document["components"]["schemas"]
        assert {
            "ProblemDetailsResponse",
            "InvalidInputProblemDetailsResponse",
            "InvalidInputErrorResponse",
        } <= set(schemas)
        assert "HTTPValidationError" not in schemas
