"""JWT access tokens issued and verified with an explicit HS256 key ring."""

from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.application.failures.invalid_access_token_failure import (
    InvalidAccessTokenFailure,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole

_ACCESS_TOKEN_ALGORITHM = "HS256"  # noqa: S105 - JWT algorithm name
"""The only algorithm accepted for first-party access tokens."""

_ACCESS_TOKEN_TYPE = "at+jwt"  # noqa: S105 - JWT media type
"""The explicit media type of an access-token JWT."""


class JwtAccessTokenCodec:
    """Issue and verify HS256 access tokens with rotating symmetric keys."""

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        signing_key_id: str,
        key_ring: dict[str, bytes],
        lifetime: timedelta,
    ) -> None:
        """Keep the fixed JWT contract and key ring.

        Args:
            issuer: The exact accepted `iss` claim.
            audience: The exact accepted `aud` claim.
            signing_key_id: The key used for new tokens.
            key_ring: Signing and verify-only keys by `kid`.
            lifetime: How long an access token works.
        """
        self._issuer = issuer
        self._audience = audience
        self._signing_key_id = signing_key_id
        self._key_ring = key_ring
        self._lifetime = lifetime

    def issue_access_token(self, claims: AccessTokenClaimsDTO) -> str:
        """Issue a signed access token for authenticated claims.

        Args:
            claims: The claims and issue time to sign.

        Returns:
            The compact JWT.
        """
        expires_at = claims.issued_at + self._lifetime
        payload = {
            "iss": self._issuer,
            "aud": self._audience,
            "sub": str(claims.owner_id),
            "sid": str(claims.session_id),
            "role": claims.role.value,
            "iat": claims.issued_at,
            "exp": expires_at,
            "jti": str(uuid4()),
        }
        return jwt.encode(
            payload,
            self._key_ring[self._signing_key_id],
            algorithm=_ACCESS_TOKEN_ALGORITHM,
            headers={"typ": _ACCESS_TOKEN_TYPE, "kid": self._signing_key_id},
        )

    def authenticate_access_token(self, access_token: str) -> AuthenticatedPrincipal:
        """Verify an access token and return its authenticated principal.

        Args:
            access_token: The compact JWT presented as a bearer credential.

        Returns:
            The principal carried by the verified token.

        Raises:
            InvalidAccessTokenFailure: The header, signature, claims, or values are invalid.
        """
        try:
            header = jwt.get_unverified_header(access_token)
            key_id = header.get("kid")
            if (
                header.get("alg") != _ACCESS_TOKEN_ALGORITHM
                or header.get("typ") != _ACCESS_TOKEN_TYPE
                or not isinstance(key_id, str)
                or key_id not in self._key_ring
            ):
                raise InvalidAccessTokenFailure

            payload: dict[str, Any] = jwt.decode(
                access_token,
                self._key_ring[key_id],
                algorithms=[_ACCESS_TOKEN_ALGORITHM],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["iss", "aud", "sub", "sid", "role", "iat", "exp", "jti"]},
            )
            subject = payload["sub"]
            session_id = payload["sid"]
            role = payload["role"]
            issued_at = payload["iat"]
            token_id = payload["jti"]
            if (
                not isinstance(subject, str)
                or not isinstance(session_id, str)
                or not isinstance(role, str)
                or not isinstance(issued_at, int)
                or isinstance(issued_at, bool)
                or not isinstance(token_id, str)
            ):
                raise InvalidAccessTokenFailure
            UUID(token_id)
            return AuthenticatedPrincipal(
                user_id=UUID(subject),
                session_id=UUID(session_id),
                role=UserRole(role),
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
            raise InvalidAccessTokenFailure from error
