"""API tests of `POST /v1/auth/sign-up` against PostgreSQL and Mailpit.

Only `utc_now` is replaced, through `app.dependency_overrides`, so each test
chooses the instant of every sign-up.
"""

import hashlib
import hmac
import logging
import os
import re
import time
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import httpx2
import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pytest_mock import MockerFixture, MockType
from sqlalchemy import Engine, create_engine, delete, insert, select
from sqlalchemy.pool import NullPool

from job_status_found.app.app import create_app
from job_status_found.features.auth.auth_settings import get_auth_settings
from job_status_found.features.auth.infrastructure.db.tables import (
    AuthEventTable,
    EmailChallengeTable,
    PasswordCredentialTable,
    UserTable,
)
from job_status_found.features.core import get_app_settings, get_utc_now

SIGN_UP_PATH = "/v1/auth/sign-up"
"""The endpoint under test."""

HMAC_KEY = "integration-test-hmac-key-with-32-plus-characters"
"""The auth HMAC key the tests configure, so they can hash a mailed code themselves."""

STUBBED_START_TIME = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The instant the stubbed `utc_now` tells unless a test moves it."""

MAILPIT_API_URL = f"http://localhost:{os.environ.get('MAILPIT_WEB_PORT', '8025')}/api/v1"
"""Mailpit's HTTP API, which lists the emails the SMTP server received."""


@pytest.fixture
def auth_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Configure the auth settings the tests rely on, and drop the cached ones around the test."""
    monkeypatch.setenv("JSF_AUTH_HMAC_KEY", HMAC_KEY)
    monkeypatch.setenv("JSF_AUTH_VERIFICATION_CODE_LIFETIME", "PT10M")
    # Only the test of the response-time floor waits for one.
    monkeypatch.setenv("JSF_AUTH_SIGN_UP_MIN_RESPONSE_TIME", "PT0S")
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


@pytest.fixture
def utc_now(mocker: MockerFixture) -> MockType:
    """Stub the current time at `STUBBED_START_TIME`; a test moves it through `return_value`."""
    utc_now = mocker.stub(name="utc_now")
    utc_now.return_value = STUBBED_START_TIME
    return utc_now


@pytest.fixture
def client(auth_settings: None, utc_now: MockType) -> Iterator[TestClient]:
    """Run a fresh application with the stubbed time, so the override leaves with it."""
    app = create_app()
    app.dependency_overrides[get_utc_now] = lambda: utc_now
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


@pytest.fixture
def database_engine(auth_settings: None) -> Iterator[Engine]:
    """Connect to the application's database, to arrange and read rows directly."""
    engine = create_engine(get_app_settings().database_url, poolclass=NullPool)
    yield engine
    engine.dispose()


@pytest.fixture
def new_mailbox_address(database_engine: Engine) -> Iterator[Callable[[], str]]:
    """Hand out unique addresses, and delete their accounts and Mailpit emails afterwards."""
    addresses: list[str] = []

    def create_mailbox_address() -> str:
        """Create a new unique address."""
        addresses.append(f"jane.{uuid4().hex}@example.com")
        return addresses[-1]

    yield create_mailbox_address
    with database_engine.begin() as connection:
        # Deleting a user keeps its events with a null user, so they go first.
        user_ids = select(UserTable.id).where(UserTable.email_normalized.in_(addresses))
        connection.execute(delete(AuthEventTable).where(AuthEventTable.user_id.in_(user_ids)))
        connection.execute(delete(UserTable).where(UserTable.email_normalized.in_(addresses)))
    for address in addresses:
        httpx2.delete(f"{MAILPIT_API_URL}/search", params={"query": f'to:"{address}"'})


@pytest.fixture
def mailbox_address(new_mailbox_address: Callable[[], str]) -> str:
    """Hand out one unique address, cleaned up after the test."""
    return new_mailbox_address()


def _post_sign_up(
    client: TestClient, email: str, *, first_name: str = "Jane", password: str = "first password"
) -> httpx2.Response:
    """Submit a sign-up for an email, with a chosen first name and password."""
    return client.post(
        SIGN_UP_PATH,
        json={"first_name": first_name, "last_name": "Doe", "email": email, "password": password},
    )


def _wait_for_emails_to(address: str, count: int) -> list[dict[str, Any]]:
    """Wait until Mailpit holds `count` emails to an address, and return them oldest first."""
    deadline = time.monotonic() + 5
    while True:
        search_result = httpx2.get(
            f"{MAILPIT_API_URL}/search", params={"query": f'to:"{address}"'}
        ).json()
        if search_result["messages_count"] >= count or time.monotonic() > deadline:
            break
        time.sleep(0.05)
    # Mailpit lists the newest message first.
    return [
        httpx2.get(f"{MAILPIT_API_URL}/message/{summary['ID']}").json()
        for summary in reversed(search_result["messages"])
    ]


def _read_verification_code_in(email: dict[str, Any]) -> str:
    """Read the 6-digit verification code from an email's text."""
    match = re.search(r"\b(\d{6})\b", str(email["Text"]))
    assert match is not None, "the email holds no 6-digit code"
    return str(match[1])


def _read_user_row(database_engine: Engine, address: str) -> Any:
    """Read the `users` row of a normalized email."""
    with database_engine.connect() as connection:
        return connection.execute(
            select(UserTable).where(UserTable.email_normalized == address)
        ).one()


def _read_password_hash(database_engine: Engine, user_id: UUID) -> str:
    """Read the stored password hash of a user."""
    with database_engine.connect() as connection:
        return connection.execute(
            select(PasswordCredentialTable.password_hash).where(
                PasswordCredentialTable.user_id == user_id
            )
        ).scalar_one()


def _read_email_challenge_rows(database_engine: Engine, user_id: UUID) -> list[Any]:
    """Read every `email_challenges` row of a user."""
    with database_engine.connect() as connection:
        return list(
            connection.execute(
                select(EmailChallengeTable).where(EmailChallengeTable.user_id == user_id)
            ).all()
        )


def _insert_verified_user(database_engine: Engine, address: str) -> None:
    """Store a verified account for an address, as if its owner confirmed a code."""
    with database_engine.begin() as connection:
        connection.execute(
            insert(UserTable).values(
                {
                    UserTable.email: address,
                    UserTable.email_normalized: address,
                    UserTable.email_verified_at: STUBBED_START_TIME,
                    UserTable.first_name: "Jane",
                    UserTable.last_name: "Doe",
                    UserTable.role: "user",
                    UserTable.created_at: STUBBED_START_TIME,
                    UserTable.updated_at: STUBBED_START_TIME,
                }
            )
        )


def _hash_verification_code(code: str) -> bytes:
    """Compute the stored hash of a code with the test's HMAC key."""
    return hmac.digest(HMAC_KEY.encode(), code.encode(), hashlib.sha256)


def test_a_new_email_stores_an_unverified_account_and_mails_its_code(
    client: TestClient, database_engine: Engine, mailbox_address: str
) -> None:
    # Given: an email no account uses.
    typed_address = mailbox_address.replace("jane.", "Jane.")

    # When: a person signs up with it.
    response = _post_sign_up(client, typed_address)

    # Then: the API accepts with an empty body.
    assert (response.status_code, response.content) == (202, b"")
    # And: an unverified account keeps the typed email and the submitted name.
    user = _read_user_row(database_engine, mailbox_address)
    assert (user.email, user.email_verified_at) == (typed_address, None)
    assert (user.first_name, user.last_name) == ("Jane", "Doe")
    # And: the password is stored only as an Argon2id hash that verifies it.
    password_hash = _read_password_hash(database_engine, user.id)
    assert password_hash.startswith("$argon2id$")
    assert PasswordHash.recommended().verify("first password", password_hash)
    # And: Mailpit receives the code, and the one open challenge holds only its
    # keyed hash, valid for the configured lifetime.
    [email] = _wait_for_emails_to(mailbox_address, 1)
    [challenge] = _read_email_challenge_rows(database_engine, user.id)
    assert challenge.purpose == "verify_email"
    assert challenge.secret_hash == _hash_verification_code(_read_verification_code_in(email))
    assert challenge.expires_at - challenge.created_at == timedelta(minutes=10)


def test_a_verified_email_answers_like_a_new_one_changes_nothing_and_mails_a_notice(
    client: TestClient, database_engine: Engine, new_mailbox_address: Callable[[], str]
) -> None:
    # Given: a verified account, and the answer a brand-new email gets.
    mailbox_address = new_mailbox_address()
    _insert_verified_user(database_engine, mailbox_address)
    user_before_sign_up = _read_user_row(database_engine, mailbox_address)
    new_email_response = _post_sign_up(client, new_mailbox_address())

    # When: someone signs up with the verified account's email.
    response = _post_sign_up(
        client, mailbox_address, first_name="Mallory", password="second password"
    )

    # Then: the answer is indistinguishable from the new email's.
    assert (response.status_code, response.headers, response.content) == (
        new_email_response.status_code,
        new_email_response.headers,
        new_email_response.content,
    )
    # And: the account is unchanged and gained no password or code.
    assert _read_user_row(database_engine, mailbox_address) == user_before_sign_up
    assert _read_email_challenge_rows(database_engine, user_before_sign_up.id) == []
    with database_engine.connect() as connection:
        credential_user_id = connection.scalar(
            select(PasswordCredentialTable.user_id).where(
                PasswordCredentialTable.user_id == user_before_sign_up.id
            )
        )
    assert credential_user_id is None
    # And: the owner is told that someone tried to sign up.
    [email] = _wait_for_emails_to(mailbox_address, 1)
    assert email["Subject"] == "You already have a JSV account"


def test_an_unverified_email_after_the_send_interval_takes_the_new_password_name_and_code(
    client: TestClient, database_engine: Engine, utc_now: MockType, mailbox_address: str
) -> None:
    # Given: an unverified account whose code was mailed an hour ago.
    _post_sign_up(client, mailbox_address)
    utc_now.return_value = STUBBED_START_TIME + timedelta(hours=1)

    # When: someone signs up again with that email.
    response = _post_sign_up(
        client, mailbox_address, first_name="Janet", password="second password"
    )

    # Then: the answer is the same empty 202.
    assert (response.status_code, response.content) == (202, b"")
    # And: the latest name and password replace the first ones.
    user = _read_user_row(database_engine, mailbox_address)
    assert user.first_name == "Janet"
    assert PasswordHash.recommended().verify(
        "second password", _read_password_hash(database_engine, user.id)
    )
    # And: only the second mailed code has a challenge.
    first_email, second_email = _wait_for_emails_to(mailbox_address, 2)
    [challenge] = _read_email_challenge_rows(database_engine, user.id)
    assert challenge.secret_hash == _hash_verification_code(
        _read_verification_code_in(second_email)
    )
    assert _read_verification_code_in(first_email) != _read_verification_code_in(second_email)


def test_a_password_outside_the_policy_answers_password_too_weak_as_a_problem(
    client: TestClient, mailbox_address: str
) -> None:
    # Given: a password too short for the policy.
    too_short = "x" * 11

    # When: a person signs up with it.
    response = _post_sign_up(client, mailbox_address, password=too_short)

    # Then: the answer is an RFC 9457 problem with the stable code and a
    # human-readable detail.
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    problem = response.json()
    assert isinstance(problem.pop("detail"), str)
    assert problem == {
        "type": "about:blank",
        "title": "Bad Request",
        "status": 400,
        "code": "password_too_weak",
    }


def test_invalid_input_answers_invalid_input_as_a_problem_without_echoing_the_password(
    client: TestClient,
) -> None:
    # Given: a body with a malformed email and no first name.
    body = {"last_name": "Doe", "email": "not-an-email", "password": "a secret password"}

    # When: it is submitted.
    response = client.post(SIGN_UP_PATH, json=body)

    # Then: the answer is a 422 problem that names each invalid field.
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    problem = response.json()
    assert problem["code"] == "invalid_input"
    assert {tuple(error["loc"]) for error in problem["errors"]} == {
        ("body", "first_name"),
        ("body", "email"),
    }
    # And: no submitted value comes back.
    assert "a secret password" not in response.text


def test_a_sign_up_logs_no_password_code_or_email(
    client: TestClient, mailbox_address: str, caplog: pytest.LogCaptureFixture
) -> None:
    # Given: every logger records at DEBUG.
    caplog.set_level(logging.DEBUG)

    # When: a person signs up and is mailed a code.
    _post_sign_up(client, mailbox_address, password="a logged password?")
    [email] = _wait_for_emails_to(mailbox_address, 1)

    # Then: no record holds the password, the code, or the address.
    logged_text = "\n".join(record.getMessage() for record in caplog.records)
    assert caplog.records, "the sign-up logged nothing, so the check proves nothing"
    for sensitive_value in (
        "a logged password?",
        _read_verification_code_in(email),
        mailbox_address,
    ):
        assert sensitive_value not in logged_text


def test_an_accepted_sign_up_answers_no_sooner_than_the_minimum_response_time(
    monkeypatch: pytest.MonkeyPatch, mailbox_address: str
) -> None:
    # Given: a minimum response time far above what a sign-up needs.
    monkeypatch.setenv("JSF_AUTH_SIGN_UP_MIN_RESPONSE_TIME", "PT0.3S")
    get_auth_settings.cache_clear()

    # When: someone signs up.
    with TestClient(create_app()) as client:
        started = time.monotonic()
        response = _post_sign_up(client, mailbox_address)
        elapsed = time.monotonic() - started

    # Then: the answer waits for the minimum.
    assert response.status_code == 202
    assert elapsed >= 0.3
