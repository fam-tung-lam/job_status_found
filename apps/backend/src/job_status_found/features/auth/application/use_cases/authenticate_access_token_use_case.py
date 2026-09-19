"""Authenticate a bearer access token without reading persistent state."""

from job_status_found.features.auth.application.ports.access_token_codec import (
    AccessTokenCodec,
    InvalidAccessToken,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.failures.access_token_authentication_failure import (
    AccessTokenAuthenticationFailure,
)


class AuthenticateAccessTokenUseCase:
    """Turn a valid access token into the application's one principal type."""

    def __init__(self, *, access_tokens: AccessTokenCodec) -> None:
        """Keep the access-token codec.

        Args:
            access_tokens: Verifies the fixed JWT contract and key ring.
        """
        self._access_tokens = access_tokens

    def invoke(self, access_token: str) -> AuthenticatedPrincipal:
        """Authenticate a bearer token without reading a table.

        Args:
            access_token: The compact bearer JWT.

        Returns:
            The token's authenticated principal.

        Raises:
            AccessTokenAuthenticationFailure: The token is not accepted.
        """
        try:
            return self._access_tokens.authenticate_access_token(access_token)
        except InvalidAccessToken as error:
            raise AccessTokenAuthenticationFailure from error
