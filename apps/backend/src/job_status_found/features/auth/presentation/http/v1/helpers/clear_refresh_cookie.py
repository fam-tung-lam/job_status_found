"""Clear the version 1 web refresh cookie after sign-out."""

from fastapi import Response

from job_status_found.features.auth.presentation.http.v1.refresh_cookie_settings import (
    REFRESH_COOKIE_PATH,
    RefreshCookieSettings,
)


def clear_refresh_cookie(response: Response, settings: RefreshCookieSettings) -> None:
    """Expire the web refresh cookie with its security attributes and path.

    Args:
        response: The sign-out response.
        settings: The cookie name and security flag.
    """
    response.set_cookie(
        key=settings.name,
        value="",
        max_age=0,
        expires=0,
        path=REFRESH_COOKIE_PATH,
        secure=settings.secure,
        httponly=True,
        samesite="strict",
    )
