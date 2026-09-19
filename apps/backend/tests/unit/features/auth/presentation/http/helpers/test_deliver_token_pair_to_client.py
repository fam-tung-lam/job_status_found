"""Unit tests of token-pair delivery through the fixed client channel."""

from datetime import timedelta

import pytest
from fastapi import Response

from job_status_found.features.auth.application.dtos.token_pair import TokenPair
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.presentation.http.helpers.deliver_token_pair_to_client import (
    deliver_token_pair_to_client,
)
from job_status_found.features.auth.presentation.http.refresh_cookie_settings import (
    RefreshCookieSettings,
)


class TestDeliverTokenPairToClient:
    """Persistent storage attributes of browser refresh cookies."""

    @pytest.mark.parametrize(
        ("is_persistent", "expected_max_age"),
        [(True, "Max-Age=2592000"), (False, None)],
        ids=["persistent", "non-persistent"],
    )
    def test_a_web_cookie_has_max_age_only_when_the_session_is_persistent(
        self, is_persistent: bool, expected_max_age: str | None
    ) -> None:
        """
        Given: a web token pair and a 30-day persistent-cookie lifetime.
        When: the pair is delivered for a persistent or non-persistent session.
        Then: only the persistent cookie carries Max-Age and JSON omits the credential.
        """
        # Given: a web token pair and a 30-day persistent-cookie lifetime.
        response = Response()
        token_pair = TokenPair(
            access_token="access-token",
            expires_in=900,
            refresh_token="refresh-token",
            client_kind=ClientKind.WEB,
            is_persistent=is_persistent,
        )
        settings = RefreshCookieSettings(
            name="jsf_refresh",
            secure=False,
            persistent_max_age=timedelta(days=30),
        )

        # When: the pair is delivered for a persistent or non-persistent session.
        body = deliver_token_pair_to_client(response, token_pair, settings)

        # Then: only the persistent cookie carries Max-Age and JSON omits the credential.
        set_cookie = response.headers["set-cookie"]
        assert ("Max-Age=" in set_cookie) is is_persistent
        if expected_max_age is not None:
            assert expected_max_age in set_cookie
        assert body.refresh_token is None
