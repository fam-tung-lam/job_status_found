"""Unit tests of the JWT access-token codec."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from job_status_found.features.auth.application.dtos.access_token_claims_dto import (
    AccessTokenClaimsDTO,
)
from job_status_found.features.auth.application.failures.invalid_access_token_failure import (
    InvalidAccessTokenFailure,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.auth.infrastructure.adapters.jwt_access_token_codec import (
    JwtAccessTokenCodec,
)

NOW = datetime.now(UTC)
"""The fixed issue time of synthetic tokens."""

KEY_A = b"a" * 32
"""The first synthetic HS256 key."""

KEY_B = b"b" * 32
"""The rotated synthetic HS256 key."""


def _valid_payload() -> dict[str, object]:
    """Build a long-lived payload with every required access-token claim."""
    return {
        "iss": "https://api.example.com",
        "aud": "job-status-found-api",
        "sub": str(uuid4()),
        "sid": str(uuid4()),
        "role": "user",
        "iat": int(NOW.timestamp()),
        "exp": int((NOW + timedelta(days=3650)).timestamp()),
        "jti": str(uuid4()),
    }


def _codec(signing_key_id: str = "a") -> JwtAccessTokenCodec:
    """Build a codec whose two keys can verify."""
    return JwtAccessTokenCodec(
        issuer="https://api.example.com",
        audience="job-status-found-api",
        signing_key_id=signing_key_id,
        key_ring={"a": KEY_A, "b": KEY_B},
        lifetime=timedelta(minutes=15),
    )


class TestJwtAccessTokenCodec:
    """HS256 issue, strict verification, and key rotation."""

    def test_an_issued_token_has_the_required_header_claims_and_principal(self) -> None:
        """
        Given: authenticated claims and key A as the signing key.
        When: the codec issues and authenticates a token.
        Then: its header, claims, lifetime, and principal match the contract.
        """
        # Given: authenticated claims and key A as the signing key.
        owner_id = uuid4()
        session_id = uuid4()
        codec = _codec()

        # When: the codec issues and authenticates a token.
        token = codec.issue_access_token(
            AccessTokenClaimsDTO(
                owner_id=owner_id,
                session_id=session_id,
                role=UserRole.USER,
                issued_at=NOW,
            )
        )
        principal = codec.authenticate_access_token(token)
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(token, KEY_A, algorithms=["HS256"], audience="job-status-found-api")

        # Then: the fixed header and required claims are present.
        assert header == {"alg": "HS256", "kid": "a", "typ": "at+jwt"}
        assert claims["iss"] == "https://api.example.com"
        assert claims["exp"] - claims["iat"] == 15 * 60
        assert {"sub", "sid", "role", "jti"} <= claims.keys()
        # And: authentication returns exactly the token principal.
        assert (principal.user_id, principal.session_id, principal.role) == (
            owner_id,
            session_id,
            UserRole.USER,
        )

    def test_a_verify_only_key_keeps_working_after_signing_rotates(self) -> None:
        """
        Given: a token signed by key A before signing moves to key B.
        When: the rotated codec authenticates the old token.
        Then: key A remains accepted as verify-only.
        """
        # Given: a token signed by key A before signing moves to key B.
        owner_id = uuid4()
        token = _codec("a").issue_access_token(
            AccessTokenClaimsDTO(
                owner_id=owner_id,
                session_id=uuid4(),
                role=UserRole.USER,
                issued_at=NOW,
            )
        )

        # When: the rotated codec authenticates the old token.
        principal = _codec("b").authenticate_access_token(token)

        # Then: key A remains accepted as verify-only.
        assert principal.user_id == owner_id

    @pytest.mark.parametrize(
        ("headers", "payload_overrides"),
        [
            ({"kid": "unknown", "typ": "at+jwt"}, {}),
            ({"typ": "at+jwt"}, {}),
            ({"kid": "a", "typ": "JWT"}, {}),
            ({"kid": "a", "typ": "at+jwt"}, {"iss": "https://wrong.example"}),
            ({"kid": "a", "typ": "at+jwt"}, {"aud": "wrong-audience"}),
            ({"kid": "a", "typ": "at+jwt"}, {"role": "superuser"}),
            ({"kid": "a", "typ": "at+jwt"}, {"sub": "not-a-uuid"}),
            ({"kid": "a", "typ": "at+jwt"}, {"sid": "not-a-uuid"}),
            ({"kid": "a", "typ": "at+jwt"}, {"iat": "not-an-integer"}),
            ({"kid": "a", "typ": "at+jwt"}, {"jti": "not-a-uuid"}),
        ],
    )
    def test_a_token_with_an_unaccepted_header_or_claim_is_rejected(
        self, headers: dict[str, str], payload_overrides: dict[str, object]
    ) -> None:
        """
        Given: a signed token with an unaccepted header or required claim.
        When: the codec authenticates it.
        Then: the token is rejected without a partial principal.
        """
        # Given: a signed token with an unaccepted header or required claim.
        payload = _valid_payload() | payload_overrides
        token = jwt.encode(payload, KEY_A, algorithm="HS256", headers=headers)

        # When: the codec authenticates it.
        # Then: the token is rejected without a partial principal.
        with pytest.raises(InvalidAccessTokenFailure):
            _codec().authenticate_access_token(token)

    def test_an_unsigned_alg_none_token_is_rejected_before_claims_are_trusted(self) -> None:
        """
        Given: an unsigned token claiming the accepted key id and media type.
        When: the codec authenticates it.
        Then: the non-HS256 algorithm is rejected.
        """
        # Given: an unsigned token claiming the accepted key id and media type.
        token = jwt.encode(
            _valid_payload(),
            key="",
            algorithm="none",
            headers={"kid": "a", "typ": "at+jwt"},
        )

        # When: the codec authenticates it.
        # Then: the non-HS256 algorithm is rejected.
        with pytest.raises(InvalidAccessTokenFailure):
            _codec().authenticate_access_token(token)

    @pytest.mark.parametrize(
        "missing_claim",
        ["iss", "aud", "sub", "sid", "role", "iat", "exp", "jti"],
    )
    def test_a_token_missing_any_required_claim_is_rejected(self, missing_claim: str) -> None:
        """
        Given: a signed token is missing one required claim.
        When: the codec authenticates it.
        Then: the incomplete token is rejected.
        """
        # Given: a signed token is missing one required claim.
        payload = _valid_payload()
        payload.pop(missing_claim)
        token = jwt.encode(
            payload,
            KEY_A,
            algorithm="HS256",
            headers={"kid": "a", "typ": "at+jwt"},
        )

        # When: the codec authenticates it.
        # Then: the incomplete token is rejected.
        with pytest.raises(InvalidAccessTokenFailure):
            _codec().authenticate_access_token(token)
