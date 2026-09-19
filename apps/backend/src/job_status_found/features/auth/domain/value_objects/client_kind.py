"""Kinds of clients that fix how refresh tokens are delivered."""

from enum import StrEnum


class ClientKind(StrEnum):
    """A client platform and its refresh-token delivery channel."""

    WEB = "web"
    """A browser, which receives the refresh token only in an HTTP-only cookie."""

    IOS = "ios"
    """An iOS app, which receives the refresh token in the response body."""

    ANDROID = "android"
    """An Android app, which receives the refresh token in the response body."""
