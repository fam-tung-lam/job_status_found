"""Response body of session creation and refresh."""

from pydantic import BaseModel, ConfigDict

from job_status_found.features.auth.domain.value_objects.auth_token_type import AuthTokenType


class TokenPairResponse(BaseModel):
    """The short-lived access token and optional mobile refresh token."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    access_token: str
    """The bearer access token."""

    expires_in: int
    """Whole seconds until the access token expires."""

    token_type: AuthTokenType = AuthTokenType.BEARER
    """The bearer token type."""

    refresh_token: str | None = None
    """The mobile refresh token; omitted for web sessions."""
