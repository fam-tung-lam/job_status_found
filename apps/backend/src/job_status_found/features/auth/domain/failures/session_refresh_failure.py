"""Failures of rotating a refresh token."""


class SessionRefreshFailure(Exception):
    """A refresh credential did not produce a new token pair."""


class SessionRefreshTokenInvalidFailure(SessionRefreshFailure):
    """No refresh-token row matches the presented credential."""

    def __init__(self) -> None:
        """Describe an unknown refresh token."""
        super().__init__("The refresh token is invalid.")


class SessionRefreshSessionEndedFailure(SessionRefreshFailure):
    """The refresh token belongs to a session that can no longer continue."""

    def __init__(self) -> None:
        """Describe an ended session without exposing its cause."""
        super().__init__("The session has ended.")


class SessionRefreshOriginNotAllowedFailure(SessionRefreshFailure):
    """A web refresh did not come from an allowed browser origin."""

    def __init__(self) -> None:
        """Describe the refused browser request."""
        super().__init__("The request origin is not allowed.")
