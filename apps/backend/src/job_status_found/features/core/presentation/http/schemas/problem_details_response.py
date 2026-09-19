"""The body of every error response."""

from pydantic import BaseModel, ConfigDict


class ProblemDetailsResponse(BaseModel):
    """An RFC 9457 problem with the stable `code` extension member.

    `type` stays `about:blank`, so `title` is the HTTP status phrase. Clients
    switch on `code`, never on `detail`.
    """

    model_config = ConfigDict(
        frozen=True,
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [
                {
                    "type": "about:blank",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "The password must have 12 to 128 characters.",
                    "code": "password_too_weak",
                }
            ]
        },
    )

    type: str = "about:blank"
    """URI of the problem type; `about:blank` means the status says it all."""

    title: str
    """The HTTP status phrase."""

    status: int
    """The HTTP status code."""

    detail: str
    """Human-readable explanation; never switch on it."""

    code: str
    """Stable machine-readable failure, such as `password_too_weak`."""
