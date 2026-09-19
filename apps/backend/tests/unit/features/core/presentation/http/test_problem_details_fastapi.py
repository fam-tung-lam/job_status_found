from fastapi import status
from pydantic import BaseModel

from job_status_found.features.core import ProblemDetailsFastAPI, problem_details_content


class _Body(BaseModel):
    """A request body, so the route can fail validation with a 422."""

    name: str


def test_the_openapi_document_describes_errors_as_problem_json() -> None:
    # Given: an app with a route that takes a body and promises a 400 problem.
    app = ProblemDetailsFastAPI()

    @app.post(
        "/things",
        responses={
            status.HTTP_400_BAD_REQUEST: {"description": "x", "content": problem_details_content()}
        },
    )
    async def create_thing(body: _Body) -> None: ...

    # When: the OpenAPI document is built.
    document = app.openapi()

    # Then: both errors name their schema under the media type the app sends,
    # and FastAPI's default validation body, which the app never sends, is gone.
    responses = document["paths"]["/things"]["post"]["responses"]
    assert responses["400"]["content"] == {
        "application/problem+json": {"schema": {"$ref": "#/components/schemas/ProblemDetails"}}
    }
    assert responses["422"]["content"] == {
        "application/problem+json": {
            "schema": {"$ref": "#/components/schemas/InvalidInputProblemDetails"}
        }
    }
    schemas = document["components"]["schemas"]
    assert {"ProblemDetails", "InvalidInputProblemDetails", "InvalidInputError"} <= set(schemas)
    assert "HTTPValidationError" not in schemas
