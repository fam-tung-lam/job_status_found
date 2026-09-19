"""Issuing and verifying this API's JWT access tokens."""

from typing import Protocol

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)


class AccessTokenCodec(Protocol):
    """Issues and verifies the API's short-lived access tokens."""

    def issue_access_token(self, claims: AccessTokenClaimsDTO) -> str:
        """Issue a signed access token for authenticated claims.

        Args:
            claims: The claims and issue time to sign.

        Returns:
            The compact JWT.
        """
        ...

    def authenticate_access_token(self, access_token: str) -> AuthenticatedPrincipal:
        """Verify an access token and return its authenticated principal.

        Args:
            access_token: The compact JWT presented as a bearer credential.

        Returns:
            The principal carried by the verified token.

        Raises:
            InvalidAccessTokenFailure: The token fails any required check.
        """
        ...
