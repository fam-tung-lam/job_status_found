"""Failure raised when an access-token codec rejects a token."""


class InvalidAccessTokenFailure(Exception):
    """The submitted value is not an access token this API accepts."""
