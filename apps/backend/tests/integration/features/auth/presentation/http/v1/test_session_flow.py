"""Version 1 API integration of confirmation, sign-in, refresh, and sign-out."""

import hashlib
import hmac
import json
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import httpx2
import jwt
import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pytest_mock import MockerFixture, MockType
from sqlalchemy import Engine, create_engine, delete, insert, select, update
from sqlalchemy.pool import NullPool

from job_status_found.app.app import create_app
from job_status_found.features.auth.auth_settings import get_auth_settings
from job_status_found.features.auth.infrastructure.db.tables import (
    AuthEventTable,
    EmailChallengeTable,
    PasswordCredentialTable,
    RefreshTokenTable,
    SessionTable,
    UserTable,
)
from job_status_found.features.core import get_app_settings, get_utc_now

NOW = datetime.now(UTC).replace(microsecond=0)
"""The current instant stubbed throughout the API flow."""

HMAC_KEY = "integration-session-flow-hmac-key-32-chars"
"""The test-only code-hashing key."""

JWT_KEY = "integration-session-flow-jwt-key-32-chars"
"""The test-only access-token signing key."""


def _encode_test_access_token(*, signing_key: str, expires_at: datetime) -> str:
    """Build a signed access token whose signature or expiry a test controls."""
    return jwt.encode(
        {
            "iss": "http://localhost:8000",
            "aud": "job-status-found-api",
            "sub": str(uuid4()),
            "sid": str(uuid4()),
            "role": "user",
            "iat": int((NOW - timedelta(minutes=30)).timestamp()),
            "exp": int(expires_at.timestamp()),
            "jti": str(uuid4()),
        },
        signing_key,
        algorithm="HS256",
        headers={"kid": "test-1", "typ": "at+jwt"},
    )


@pytest.fixture
def session_auth_settings(
    test_database_configured: None, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """Configure all auth secrets and local insecure-cookie values for this flow."""
    monkeypatch.setenv("JSF_AUTH_HMAC_KEY", HMAC_KEY)
    monkeypatch.setenv("JSF_AUTH_JWT_SIGNING_KEY_ID", "test-1")
    monkeypatch.setenv("JSF_AUTH_JWT_KEY_RING", json.dumps({"test-1": JWT_KEY}))
    monkeypatch.setenv("JSF_AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("JSF_AUTH_REFRESH_COOKIE_NAME", "jsf_refresh")
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


@pytest.fixture
def utc_now(mocker: MockerFixture) -> MockType:
    """Stub the business clock at `NOW`."""
    stub = mocker.stub(name="utc_now")
    stub.return_value = NOW
    return stub


@pytest.fixture
def client(session_auth_settings: None, utc_now: MockType) -> Iterator[TestClient]:
    """Run a fresh application with deterministic business time."""
    app = create_app()
    app.dependency_overrides[get_utc_now] = lambda: utc_now
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


@pytest.fixture
def database_engine(session_auth_settings: None) -> Iterator[Engine]:
    """Connect to the disposable API-test database."""
    engine = create_engine(get_app_settings().database_url, poolclass=NullPool)
    yield engine
    engine.dispose()


@pytest.fixture
def unverified_password_account(database_engine: Engine) -> Iterator[tuple[str, UUID]]:
    """Store one unverified password account and open code, then delete it."""
    email = f"session.{uuid4().hex}@example.com"
    owner_id = uuid4()
    challenge_id = uuid4()
    password_hash = PasswordHash.recommended().hash("matching password")
    code_hash = hmac.digest(HMAC_KEY.encode(), b"123456", hashlib.sha256)
    with database_engine.begin() as connection:
        connection.execute(
            insert(UserTable).values(
                id=owner_id,
                email=email,
                email_normalized=email,
                email_verified_at=None,
                first_name="Jane",
                last_name="Doe",
                avatar_url=None,
                locale=None,
                role="user",
                suspended_at=None,
                deletion_requested_at=None,
                created_at=NOW,
                updated_at=NOW,
            )
        )
        connection.execute(
            insert(PasswordCredentialTable).values(
                user_id=owner_id,
                password_hash=password_hash,
                created_at=NOW,
                updated_at=NOW,
            )
        )
        connection.execute(
            insert(EmailChallengeTable).values(
                id=challenge_id,
                user_id=owner_id,
                purpose="verify_email",
                secret_hash=code_hash,
                new_email=None,
                attempt_count=0,
                created_at=NOW,
                expires_at=NOW + timedelta(minutes=15),
                consumed_at=None,
            )
        )
    yield email, owner_id
    with database_engine.begin() as connection:
        connection.execute(delete(AuthEventTable).where(AuthEventTable.user_id == owner_id))
        connection.execute(delete(UserTable).where(UserTable.id == owner_id))


class TestSessionFlow:
    """The real API, PostgreSQL repositories, Argon2id, HMAC, and JWT codec together."""

    @pytest.mark.parametrize(
        ("signing_key", "expires_at"),
        [
            ("wrong-signing-key-with-at-least-32-characters", NOW + timedelta(minutes=15)),
            (JWT_KEY, NOW - timedelta(seconds=1)),
        ],
        ids=["wrongly-signed", "expired"],
    )
    def test_wrongly_signed_and_expired_access_tokens_return_the_bearer_failure(
        self,
        client: TestClient,
        signing_key: str,
        expires_at: datetime,
    ) -> None:
        """
        Given: an access token with a wrong signature or elapsed expiry.
        When: it calls the authenticated current-user endpoint.
        Then: the API returns the stable bearer failure and challenge.
        """
        # Given: an access token with a wrong signature or elapsed expiry.
        access_token = _encode_test_access_token(signing_key=signing_key, expires_at=expires_at)

        # When: it calls the authenticated current-user endpoint.
        response = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})

        # Then: the API returns the stable bearer failure and challenge.
        assert (response.status_code, response.json()["code"]) == (
            401,
            "access_token_invalid",
        )
        assert response.headers["www-authenticate"] == "Bearer"

    def test_confirmation_me_refresh_sign_out_and_password_sign_in_share_one_contract(
        self,
        client: TestClient,
        database_engine: Engine,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: an unverified password account with a live emailed code.
        When: the owner confirms, reads `/me`, refreshes, signs out, and signs in again.
        Then: each endpoint persists and returns the session contract expected by the app.
        """
        # Given: an unverified password account with a live emailed code.
        email, owner_id = unverified_password_account

        # When: the owner confirms the code and its matching password on Android.
        confirmation = client.post(
            "/v1/auth/email-verification/confirm",
            json={
                "email": email,
                "code": "123456",
                "password": "matching password",
                "client_kind": "android",
                "remember_me": True,
            },
        )

        # Then: both credentials are returned and only the refresh hash is stored.
        assert confirmation.status_code == 200
        first_tokens = confirmation.json()
        assert first_tokens["token_type"] == "Bearer"
        assert "refresh_token" in first_tokens
        with database_engine.connect() as connection:
            user = connection.execute(select(UserTable).where(UserTable.id == owner_id)).one()
            [session] = connection.execute(
                select(SessionTable).where(SessionTable.user_id == owner_id)
            ).all()
            [stored_refresh_hash] = connection.scalars(
                select(RefreshTokenTable.token_hash).where(
                    RefreshTokenTable.session_id == session.id
                )
            ).all()
        assert user.email_verified_at == NOW
        assert (
            stored_refresh_hash == hashlib.sha256(first_tokens["refresh_token"].encode()).digest()
        )

        # When: the access token reads the current user.
        current_user = client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {first_tokens['access_token']}"},
        )

        # Then: `/me` exposes the fixed frontend contract and no credential.
        assert current_user.status_code == 200
        assert current_user.json() == {
            "id": str(owner_id),
            "email": email,
            "first_name": "Jane",
            "last_name": "Doe",
            "avatar_url": None,
            "locale": None,
            "role": "user",
            "has_password": True,
            "linked_providers": [],
        }

        # When: the mobile refresh token rotates and its replacement signs out.
        refresh = client.post(
            "/v1/auth/token/refresh",
            json={"refresh_token": first_tokens["refresh_token"]},
        )
        assert refresh.status_code == 200
        second_tokens = refresh.json()
        assert second_tokens["refresh_token"] != first_tokens["refresh_token"]
        sign_out = client.post(
            "/v1/auth/sign-out",
            json={"refresh_token": second_tokens["refresh_token"]},
        )

        # Then: sign-out is empty and the rotated credential reports an ended session.
        assert (sign_out.status_code, sign_out.content) == (204, b"")
        ended = client.post(
            "/v1/auth/token/refresh",
            json={"refresh_token": second_tokens["refresh_token"]},
        )
        assert (ended.status_code, ended.json()["code"]) == (401, "session_ended")

        # When: the same account signs in again with its password.
        sign_in = client.post(
            "/v1/auth/sign-in",
            json={
                "email": email,
                "password": "matching password",
                "client_kind": "ios",
                "remember_me": True,
            },
        )

        # Then: password sign-in opens another mobile session without applying a new-password rule.
        assert sign_in.status_code == 200
        assert "refresh_token" in sign_in.json()

        # And: an unknown refresh credential falls back to its valid bearer token.
        bearer_sign_out = client.post(
            "/v1/auth/sign-out",
            headers={"Authorization": f"Bearer {sign_in.json()['access_token']}"},
            json={"refresh_token": "unknown-refresh-token"},
        )
        assert (bearer_sign_out.status_code, bearer_sign_out.content) == (204, b"")
        bearer_session_ended = client.post(
            "/v1/auth/token/refresh",
            json={"refresh_token": sign_in.json()["refresh_token"]},
        )
        assert (bearer_session_ended.status_code, bearer_session_ended.json()["code"]) == (
            401,
            "session_ended",
        )

    def test_a_non_persistent_web_session_uses_only_the_strict_http_only_cookie(
        self,
        client: TestClient,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: an unverified password account with a live code.
        When: the owner confirms as a non-persistent web client.
        Then: the refresh token is absent from JSON and uses the exact session-cookie attributes.
        And: refresh requires an allowed Origin and rotates the cookie.
        """
        # Given: an unverified password account with a live code.
        email, _owner_id = unverified_password_account

        # When: the owner confirms as a non-persistent web client.
        confirmation = client.post(
            "/v1/auth/email-verification/confirm",
            json={
                "email": email,
                "code": "123456",
                "password": "matching password",
                "client_kind": "web",
                "remember_me": False,
            },
        )

        # Then: the refresh token is absent from JSON and uses the strict HTTP-only cookie.
        assert confirmation.status_code == 200
        assert "refresh_token" not in confirmation.json()
        set_cookie = confirmation.headers["set-cookie"]
        assert "jsf_refresh=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=strict" in set_cookie
        assert "Path=/v1/auth" in set_cookie
        assert "Max-Age" not in set_cookie
        assert "Secure" not in set_cookie

        # When: the cookie is refreshed without an Origin and then with an allowed one.
        refused = client.post("/v1/auth/token/refresh")
        rotated = client.post("/v1/auth/token/refresh", headers={"Origin": "http://localhost:3000"})

        # Then: only the allowed browser Origin rotates the HTTP-only cookie.
        assert (refused.status_code, refused.json()["code"]) == (403, "origin_not_allowed")
        assert rotated.status_code == 200
        assert "refresh_token" not in rotated.json()
        assert "jsf_refresh=" in rotated.headers["set-cookie"]

        # And: cookie sign-out with the allowed Origin revokes and expires the cookie.
        signed_out = client.post("/v1/auth/sign-out", headers={"Origin": "http://localhost:3000"})
        assert (signed_out.status_code, signed_out.content) == (204, b"")
        cleared_cookie = signed_out.headers["set-cookie"]
        assert "jsf_refresh=" in cleared_cookie
        assert "Max-Age=0" in cleared_cookie
        assert "HttpOnly" in cleared_cookie
        assert "SameSite=strict" in cleared_cookie
        assert "Path=/v1/auth" in cleared_cookie

    def test_the_default_web_cookie_uses_the_secure_reserved_name(
        self,
        unverified_password_account: tuple[str, UUID],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        utc_now: MockType,
    ) -> None:
        """
        Given: auth uses its default production cookie settings.
        When: email confirmation opens a web session.
        Then: the response sets the `__Secure-` cookie with the Secure attribute.
        """
        # Given: auth uses its default production cookie settings.
        email, _owner_id = unverified_password_account
        monkeypatch.delenv("JSF_AUTH_COOKIE_SECURE", raising=False)
        monkeypatch.delenv("JSF_AUTH_REFRESH_COOKIE_NAME", raising=False)
        monkeypatch.chdir(tmp_path)
        get_auth_settings.cache_clear()
        app = create_app()
        app.dependency_overrides[get_utc_now] = lambda: utc_now

        # When: email confirmation opens a web session.
        with TestClient(app, follow_redirects=False) as secure_client:
            confirmation = secure_client.post(
                "/v1/auth/email-verification/confirm",
                json={
                    "email": email,
                    "code": "123456",
                    "password": "matching password",
                    "client_kind": "web",
                    "remember_me": True,
                },
            )

        # Then: the response sets the `__Secure-` cookie with the Secure attribute.
        assert confirmation.status_code == 200
        set_cookie = confirmation.headers["set-cookie"]
        assert "__Secure-jsf_refresh=" in set_cookie
        assert "Secure" in set_cookie

    def test_an_unknown_refresh_token_returns_the_generic_refresh_failure(
        self, client: TestClient
    ) -> None:
        """
        Given: a refresh credential whose hash has no database row.
        When: it is submitted to the refresh endpoint.
        Then: the API returns refresh_token_invalid and a bearer challenge.
        """
        # Given: a refresh credential whose hash has no database row.
        # When: it is submitted to the refresh endpoint.
        response = client.post(
            "/v1/auth/token/refresh",
            json={"refresh_token": "unknown-refresh-token"},
        )

        # Then: the API returns refresh_token_invalid and a bearer challenge.
        assert (response.status_code, response.json()["code"]) == (
            401,
            "refresh_token_invalid",
        )
        assert response.headers["www-authenticate"] == "Bearer"

    def test_an_expired_refresh_token_returns_session_ended(
        self,
        client: TestClient,
        database_engine: Engine,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: a known mobile refresh token has reached its expiry.
        When: it is submitted to the refresh endpoint.
        Then: the API returns session_ended and a bearer challenge.
        """
        # Given: a known mobile refresh token has reached its expiry.
        email, _owner_id = unverified_password_account
        confirmation = client.post(
            "/v1/auth/email-verification/confirm",
            json={
                "email": email,
                "code": "123456",
                "password": "matching password",
                "client_kind": "android",
                "remember_me": True,
            },
        )
        assert confirmation.status_code == 200
        refresh_token = confirmation.json()["refresh_token"]
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).digest()
        with database_engine.begin() as connection:
            connection.execute(
                update(RefreshTokenTable)
                .where(RefreshTokenTable.token_hash == refresh_token_hash)
                .values(expires_at=NOW)
            )

        # When: it is submitted to the refresh endpoint.
        response = client.post(
            "/v1/auth/token/refresh",
            json={"refresh_token": refresh_token},
        )

        # Then: the API returns session_ended and a bearer challenge.
        assert (response.status_code, response.json()["code"]) == (401, "session_ended")
        assert response.headers["www-authenticate"] == "Bearer"

    def test_two_concurrent_refreshes_cannot_both_create_an_active_normal_child(
        self,
        client: TestClient,
        database_engine: Engine,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: one unused mobile refresh token.
        When: two real requests submit it concurrently against PostgreSQL.
        Then: the token is spent once and only one child remains active.
        And: the grace retry revokes the other child instead of passing normal rotation twice.
        """
        # Given: one unused mobile refresh token.
        email, owner_id = unverified_password_account
        confirmation = client.post(
            "/v1/auth/email-verification/confirm",
            json={
                "email": email,
                "code": "123456",
                "password": "matching password",
                "client_kind": "android",
                "remember_me": True,
            },
        )
        assert confirmation.status_code == 200
        parent_token = confirmation.json()["refresh_token"]
        parent_hash = hashlib.sha256(parent_token.encode()).digest()
        starting_barrier = Barrier(3)

        def refresh_at_the_barrier() -> httpx2.Response:
            """Submit the shared parent after both worker threads are ready."""
            starting_barrier.wait()
            return client.post("/v1/auth/token/refresh", json={"refresh_token": parent_token})

        # When: two real requests submit it concurrently against PostgreSQL.
        with ThreadPoolExecutor(max_workers=2) as executor:
            first_future = executor.submit(refresh_at_the_barrier)
            second_future = executor.submit(refresh_at_the_barrier)
            starting_barrier.wait()
            responses = [first_future.result(), second_future.result()]

        # Then: both protocol responses succeed through normal rotation then grace retry.
        assert [response.status_code for response in responses] == [200, 200]
        response_token_hashes = {
            hashlib.sha256(response.json()["refresh_token"].encode()).digest()
            for response in responses
        }
        with database_engine.connect() as connection:
            parent = connection.execute(
                select(RefreshTokenTable).where(RefreshTokenTable.token_hash == parent_hash)
            ).one()
            children = connection.execute(
                select(RefreshTokenTable)
                .where(RefreshTokenTable.parent_token_id == parent.id)
                .order_by(RefreshTokenTable.created_at)
            ).all()
            session = connection.execute(
                select(SessionTable).where(SessionTable.user_id == owner_id)
            ).one()

        # And: the parent was spent once, one returned child was revoked, one is active,
        # and replay grace did not end the session.
        assert parent.used_at == NOW
        assert len(children) == 2
        assert {child.token_hash for child in children} == response_token_hashes
        assert sum(child.revoked_at is None for child in children) == 1
        assert session.revoked_at is None

    def test_password_sign_in_hides_account_state_until_the_password_is_proved(
        self,
        client: TestClient,
        database_engine: Engine,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: an unverified password account with a code sent inside the resend interval.
        When: the right and wrong passwords are submitted.
        Then: only the right password reveals verification is required.
        And: the wrong password records one identifier-hashed failure without raw credentials.
        """
        # Given: an unverified password account with a recently sent code.
        email, owner_id = unverified_password_account
        base_body = {
            "email": email,
            "client_kind": "android",
            "remember_me": True,
        }

        # When: the right and wrong passwords are submitted.
        right_password = client.post(
            "/v1/auth/sign-in", json=base_body | {"password": "matching password"}
        )
        wrong_password = client.post(
            "/v1/auth/sign-in", json=base_body | {"password": "wrong password"}
        )

        # Then: only the right password reveals verification is required.
        assert (right_password.status_code, right_password.json()["code"]) == (
            403,
            "email_verification_required",
        )
        assert (wrong_password.status_code, wrong_password.json()["code"]) == (
            401,
            "invalid_credentials",
        )

        # And: the wrong password records one identifier-hashed failure without raw credentials.
        with database_engine.connect() as connection:
            [event] = connection.execute(
                select(AuthEventTable).where(
                    AuthEventTable.user_id == owner_id,
                    AuthEventTable.event_type == "sign_in_failed",
                )
            ).all()
        assert event.identifier_hash is not None
        assert event.identifier_hash != email.encode()
        assert event.details is None

    def test_a_suspended_account_is_disclosed_only_after_the_password_matches(
        self,
        client: TestClient,
        database_engine: Engine,
        unverified_password_account: tuple[str, UUID],
    ) -> None:
        """
        Given: a verified suspended password account.
        When: the right and wrong passwords are submitted.
        Then: only the right password reports account_unavailable.
        """
        # Given: a verified suspended password account.
        email, owner_id = unverified_password_account
        with database_engine.begin() as connection:
            connection.execute(
                update(UserTable)
                .where(UserTable.id == owner_id)
                .values(email_verified_at=NOW, suspended_at=NOW)
            )
        base_body = {
            "email": email,
            "client_kind": "ios",
            "remember_me": True,
        }

        # When: the right and wrong passwords are submitted.
        right_password = client.post(
            "/v1/auth/sign-in", json=base_body | {"password": "matching password"}
        )
        wrong_password = client.post(
            "/v1/auth/sign-in", json=base_body | {"password": "wrong password"}
        )

        # Then: only the right password reports account_unavailable.
        assert (right_password.status_code, right_password.json()["code"]) == (
            403,
            "account_unavailable",
        )
        assert (wrong_password.status_code, wrong_password.json()["code"]) == (
            401,
            "invalid_credentials",
        )
