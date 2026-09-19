"""Optional version 1 mobile request body of refresh and sign-out."""

from pydantic import BaseModel, ConfigDict


class RefreshSessionRequest(BaseModel):
    """The body-delivered refresh credential of an iOS or Android session."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    refresh_token: str
    """The opaque mobile refresh token."""
