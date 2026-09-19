"""One field that failed validation."""

from pydantic import BaseModel, ConfigDict


class InvalidInputErrorResponse(BaseModel):
    """One field that failed validation, without the value that was sent."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    loc: list[str | int]
    """Where the field is, such as `["body", "email"]`."""

    msg: str
    """Human-readable reason."""

    type: str
    """Stable Pydantic error type, such as `missing` or `value_error`."""
