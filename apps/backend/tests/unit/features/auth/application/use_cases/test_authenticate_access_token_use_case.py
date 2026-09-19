"""Unit tests of stateless access-token authentication."""

from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.ports.access_token_codec import (
    AccessTokenCodec,
    InvalidAccessToken,
)
from job_status_found.features.auth.application.use_cases.authenticate_access_token_use_case import (  # noqa: E501
    AuthenticateAccessTokenUseCase,
)
from job_status_found.features.auth.domain.entities.authenticated_principal import (
    AuthenticatedPrincipal,
)
from job_status_found.features.auth.domain.failures.access_token_authentication_failure import (
    AccessTokenAuthenticationFailure,
)
from job_status_found.features.auth.domain.value_objects.user_role import UserRole


class TestAuthenticateAccessTokenUseCase:
    """The codec boundary and generic domain failure."""

    def test_a_valid_token_returns_its_principal_without_another_collaborator(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: the codec accepts an access token.
        When: the use case authenticates it.
        Then: the codec's principal is returned unchanged.
        """
        # Given: the codec accepts an access token.
        codec = mocker.create_autospec(AccessTokenCodec, instance=True)
        principal = AuthenticatedPrincipal(uuid4(), uuid4(), UserRole.USER)
        codec.authenticate_access_token.return_value = principal

        # When: the use case authenticates it.
        result = AuthenticateAccessTokenUseCase(access_tokens=codec).invoke("token")

        # Then: the codec's principal is returned unchanged.
        assert result == principal

    def test_any_codec_rejection_becomes_the_one_access_token_failure(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: the codec rejects a malformed token.
        When: the use case authenticates it.
        Then: callers receive the generic access-token failure.
        """
        # Given: the codec rejects a malformed token.
        codec = mocker.create_autospec(AccessTokenCodec, instance=True)
        codec.authenticate_access_token.side_effect = InvalidAccessToken

        # When: the use case authenticates it.
        # Then: callers receive the generic access-token failure.
        with pytest.raises(AccessTokenAuthenticationFailure):
            AuthenticateAccessTokenUseCase(access_tokens=codec).invoke("bad")
