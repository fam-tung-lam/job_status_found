"""Failures of authenticating a bearer access token."""


class AccessTokenAuthenticationFailure(Exception):
    """A bearer credential is missing or not an accepted access token."""

    def __init__(self) -> None:
        """Describe the deliberately non-specific bearer failure."""
        super().__init__("A valid bearer access token is required.")
