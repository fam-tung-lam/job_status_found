"""Credentials issued for one authenticated session."""

from dataclasses import dataclass

from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind


@dataclass(frozen=True, slots=True)
class TokenPair:
    """An access token and the refresh credential for its client channel."""

    access_token: str
    """The short-lived bearer access token."""

    expires_in: int
    """Whole seconds until the access token expires."""

    refresh_token: str
    """The opaque refresh token; presentation omits it for web clients."""

    client_kind: ClientKind
    """The channel that decides how the refresh token is delivered."""

    is_persistent: bool
    """Whether a web cookie gets a `Max-Age`."""
