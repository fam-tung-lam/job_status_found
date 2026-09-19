"""Deliver a token pair through the channel fixed by its client kind."""

from fastapi import Response

from job_status_found.features.auth.application.dtos.token_pair import TokenPair
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.presentation.http.refresh_cookie_settings import (
    REFRESH_COOKIE_PATH,
    RefreshCookieSettings,
)
from job_status_found.features.auth.presentation.http.schemas.token_pair_response import (
    TokenPairResponse,
)


def deliver_token_pair_to_client(
    response: Response, token_pair: TokenPair, settings: RefreshCookieSettings
) -> TokenPairResponse:
    """Put a refresh token in exactly the channel fixed by its session.

    Args:
        response: The response whose cookie may be set.
        token_pair: The issued credentials and fixed client kind.
        settings: The cookie name, security flag, and persistent lifetime.

    Returns:
        The JSON response, omitting the web refresh credential.
    """
    if token_pair.client_kind is ClientKind.WEB:
        response.set_cookie(
            key=settings.name,
            value=token_pair.refresh_token,
            max_age=(
                int(settings.persistent_max_age.total_seconds())
                if token_pair.is_persistent
                else None
            ),
            path=REFRESH_COOKIE_PATH,
            secure=settings.secure,
            httponly=True,
            samesite="strict",
        )
        refresh_token = None
    else:
        refresh_token = token_pair.refresh_token
    return TokenPairResponse(
        access_token=token_pair.access_token,
        expires_in=token_pair.expires_in,
        refresh_token=refresh_token,
    )
