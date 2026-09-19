"""Integration tests of revision `0001` against throwaway PostgreSQL databases."""

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Connection, Engine, create_engine, delete, func, insert, select, text
from sqlalchemy import inspect as inspect_database
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool

from job_status_found.app.alembic_metadata import metadata
from job_status_found.features.core import AppSettings

NOW = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)
"""The instant every timestamp column of an inserted row holds."""

type RowBuilder = Callable[[Connection, Mapping[str, object]], dict[str, object]]
"""Builds valid values for one table's row from the values a test supplies."""


@contextmanager
def _throwaway_database() -> Iterator[URL]:
    """Create an empty database on the configured server, and drop it afterwards."""
    server_url = AppSettings().database_url
    database_name = f"jsf_test_{uuid4().hex}"
    admin_engine = create_engine(server_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        try:
            yield server_url.set(database=database_name)
        finally:
            with admin_engine.connect() as connection:
                connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))
    finally:
        admin_engine.dispose()


def _run_alembic(
    engine: Engine, project_root: Path, alembic_command: Callable[[Config], None]
) -> None:
    """Run one Alembic command through `migrations/env.py` on the engine's database."""
    with engine.begin() as connection:
        config = Config(str(project_root / "alembic.ini"), attributes={"connection": connection})
        alembic_command(config)


def _upgrade_to_head(config: Config) -> None:
    """Upgrade the database to the newest revision."""
    command.upgrade(config, "head")


def _downgrade_to_base(config: Config) -> None:
    """Downgrade the database to before the first revision."""
    command.downgrade(config, "base")


@pytest.fixture
def empty_database() -> Iterator[Engine]:
    """Connect to a new empty database, dropped after the test."""
    with _throwaway_database() as url:
        engine = create_engine(url, poolclass=NullPool)
        yield engine
        engine.dispose()


@pytest.fixture(scope="module")
def migrated_database(pytestconfig: pytest.Config) -> Iterator[Engine]:
    """Connect to a new database at the head revision, shared by the module's tests."""
    with _throwaway_database() as url:
        engine = create_engine(url, poolclass=NullPool)
        _run_alembic(engine, pytestconfig.rootpath, _upgrade_to_head)
        yield engine
        engine.dispose()


@pytest.fixture
def connection(migrated_database: Engine) -> Iterator[Connection]:
    """Open a transaction on the migrated database and roll it back after the test.

    The rollback is what lets the tests share one migrated database.
    """
    with migrated_database.connect() as connection:
        transaction = connection.begin()
        yield connection
        transaction.rollback()


def _parent(
    connection: Connection, given: Mapping[str, object], column: str, table_name: str
) -> dict[str, object]:
    """Insert the parent row a column references, unless the test supplied it."""
    return {} if column in given else {column: _insert(connection, table_name)}


def _user_row(_connection: Connection, _given: Mapping[str, object]) -> dict[str, object]:
    """Build valid `users` values with a unique email."""
    email = f"{uuid4().hex}@example.com"
    return {
        "email": email,
        "email_normalized": email,
        "role": "user",
        "terms_version": "2026-09-18",
        "terms_accepted_at": NOW,
        "created_at": NOW,
        "updated_at": NOW,
    }


def _password_credential_row(
    connection: Connection, given: Mapping[str, object]
) -> dict[str, object]:
    """Build valid `password_credentials` values, inserting their user if needed."""
    return _parent(connection, given, "user_id", "users") | {
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$aGFzaA",
        "created_at": NOW,
        "updated_at": NOW,
    }


def _external_identity_row(
    connection: Connection, given: Mapping[str, object]
) -> dict[str, object]:
    """Build valid `external_identities` values, inserting their user if needed."""
    return _parent(connection, given, "user_id", "users") | {
        "provider": "google",
        "provider_subject": uuid4().hex,
        "email_verified": True,
        "created_at": NOW,
    }


def _session_row(connection: Connection, given: Mapping[str, object]) -> dict[str, object]:
    """Build valid `sessions` values, inserting their user if needed."""
    return _parent(connection, given, "user_id", "users") | {
        "sign_in_method": "password",
        "client_kind": "web",
        "is_persistent": False,
        "created_at": NOW,
        "authenticated_at": NOW,
        "last_refreshed_at": NOW,
        "idle_expires_at": NOW + timedelta(hours=24),
        "absolute_expires_at": NOW + timedelta(days=7),
    }


def _refresh_token_row(connection: Connection, given: Mapping[str, object]) -> dict[str, object]:
    """Build valid `refresh_tokens` values, inserting their session if needed."""
    return _parent(connection, given, "session_id", "sessions") | {
        "token_hash": uuid4().bytes,
        "created_at": NOW,
        "expires_at": NOW + timedelta(hours=24),
    }


def _email_challenge_row(connection: Connection, given: Mapping[str, object]) -> dict[str, object]:
    """Build valid `email_challenges` values, inserting their user if needed."""
    return _parent(connection, given, "user_id", "users") | {
        "purpose": "verify_email",
        "secret_hash": uuid4().bytes,
        "attempt_count": 0,
        "created_at": NOW,
        "expires_at": NOW + timedelta(minutes=15),
    }


def _oauth_authorization_attempt_row(
    _connection: Connection, _given: Mapping[str, object]
) -> dict[str, object]:
    """Build valid `oauth_authorization_attempts` values with unique hashes."""
    return {
        "provider": "google",
        "purpose": "sign_in",
        "client_kind": "web",
        "state_hash": uuid4().bytes,
        "nonce": uuid4().hex,
        "client_redirect_uri": "https://app.example.com/auth.html",
        "client_code_challenge": uuid4().hex,
        "created_at": NOW,
        "expires_at": NOW + timedelta(minutes=10),
    }


def _auth_event_row(_connection: Connection, _given: Mapping[str, object]) -> dict[str, object]:
    """Build valid `auth_events` values without a user, as for an attempt before sign-in."""
    return {"event_type": "sign_in_failed", "created_at": NOW}


_ROW_BUILDERS: dict[str, RowBuilder] = {
    "users": _user_row,
    "password_credentials": _password_credential_row,
    "external_identities": _external_identity_row,
    "sessions": _session_row,
    "refresh_tokens": _refresh_token_row,
    "email_challenges": _email_challenge_row,
    "oauth_authorization_attempts": _oauth_authorization_attempt_row,
    "auth_events": _auth_event_row,
}
"""The builder of valid values for each table, so `_insert` can fill any row."""


def _insert(connection: Connection, table_name: str, **given: object) -> UUID:
    """Insert a valid row, with `given` overriding its values, and return its key."""
    table = metadata.tables[table_name]
    row = _ROW_BUILDERS[table_name](connection, given) | given
    key_column = next(iter(table.primary_key.columns))
    key = connection.execute(insert(table).values(row).returning(key_column)).scalar_one()
    assert isinstance(key, UUID)
    return key


def _stored_value(connection: Connection, table_name: str, row_id: UUID, column: str) -> object:
    """Read one column of the row with a key."""
    table = metadata.tables[table_name]
    key_column = next(iter(table.primary_key.columns))
    return connection.execute(select(table.c[column]).where(key_column == row_id)).scalar_one()


def _count(connection: Connection, table_name: str) -> int:
    """Count the rows of a table."""
    return connection.execute(
        select(func.count()).select_from(metadata.tables[table_name])
    ).scalar_one()


def test_upgrade_creates_exactly_the_schema_the_mapped_tables_declare(
    empty_database: Engine, pytestconfig: pytest.Config
) -> None:
    # Given: an empty database.

    # When: the migration history runs up to its head.
    _run_alembic(empty_database, pytestconfig.rootpath, _upgrade_to_head)

    # Then: `alembic check` finds no difference between the upgraded schema and
    # the mapped tables; it raises `AutogenerateDiffsDetected` when it does.
    _run_alembic(empty_database, pytestconfig.rootpath, command.check)


def test_downgrade_to_base_removes_every_auth_table(
    empty_database: Engine, pytestconfig: pytest.Config
) -> None:
    # Given: a database at the head revision.
    _run_alembic(empty_database, pytestconfig.rootpath, _upgrade_to_head)

    # When: the history is downgraded to its base.
    _run_alembic(empty_database, pytestconfig.rootpath, _downgrade_to_base)

    # Then: only Alembic's own version table remains.
    assert set(inspect_database(empty_database).get_table_names()) == {"alembic_version"}


def test_deleting_a_user_deletes_its_rows_and_keeps_its_audit_events_anonymous(
    connection: Connection,
) -> None:
    # Given: a user with a row in every table that references users.
    user_id = _insert(connection, "users")
    _insert(connection, "password_credentials", user_id=user_id)
    _insert(connection, "external_identities", user_id=user_id)
    session_id = _insert(connection, "sessions", user_id=user_id)
    _insert(connection, "refresh_tokens", session_id=session_id)
    _insert(connection, "email_challenges", user_id=user_id)
    _insert(connection, "oauth_authorization_attempts", purpose="link", initiating_user_id=user_id)
    _insert(connection, "oauth_authorization_attempts", resolved_user_id=user_id)
    event_id = _insert(connection, "auth_events", user_id=user_id)
    users = metadata.tables["users"]
    auth_events = metadata.tables["auth_events"]

    # When: the user is deleted.
    connection.execute(delete(users).where(users.c.id == user_id))

    # Then: only the audit event remains, and it no longer names the user.
    assert {name: _count(connection, name) for name in metadata.tables} == {
        name: 1 if name == "auth_events" else 0 for name in metadata.tables
    }
    event_user_id = connection.execute(
        select(auth_events.c.user_id).where(auth_events.c.id == event_id)
    ).scalar_one()
    assert event_user_id is None


def test_deleting_a_session_deletes_its_refresh_tokens(connection: Connection) -> None:
    # Given: a session with a refresh token.
    session_id = _insert(connection, "sessions")
    _insert(connection, "refresh_tokens", session_id=session_id)
    sessions = metadata.tables["sessions"]

    # When: the session is deleted, as the purge does.
    connection.execute(delete(sessions).where(sessions.c.id == session_id))

    # Then: its refresh tokens are gone too.
    assert _count(connection, "refresh_tokens") == 0


def test_deleting_a_parent_refresh_token_keeps_its_child(connection: Connection) -> None:
    # Given: a refresh token that replaced an earlier one.
    session_id = _insert(connection, "sessions")
    parent_id = _insert(connection, "refresh_tokens", session_id=session_id)
    child_id = _insert(
        connection, "refresh_tokens", session_id=session_id, parent_token_id=parent_id
    )
    refresh_tokens = metadata.tables["refresh_tokens"]

    # When: the expired parent is deleted, as the purge does.
    connection.execute(delete(refresh_tokens).where(refresh_tokens.c.id == parent_id))

    # Then: the child remains and no longer points at a parent.
    child_parent_id = connection.execute(
        select(refresh_tokens.c.parent_token_id).where(refresh_tokens.c.id == child_id)
    ).scalar_one()
    assert child_parent_id is None


def test_a_user_has_at_most_one_password_credential(connection: Connection) -> None:
    # Given: a user with a password.
    user_id = _insert(connection, "users")
    _insert(connection, "password_credentials", user_id=user_id)

    # When: a second password credential is stored for the same user.
    # Then: the database rejects it through the table's primary key.
    with (
        pytest.raises(IntegrityError, match="pk_password_credentials"),
        connection.begin_nested(),
    ):
        _insert(connection, "password_credentials", user_id=user_id)


@pytest.mark.parametrize(
    ("revoked_at", "revocation_reason"),
    [(None, None), (NOW, "signed_out")],
    ids=["open", "revoked"],
)
def test_a_session_accepts_a_revocation_reason_exactly_when_revoked(
    connection: Connection, revoked_at: datetime | None, revocation_reason: str | None
) -> None:
    # Given: the migrated database.

    # When: a session is stored with a matching revocation instant and reason.
    session_id = _insert(
        connection, "sessions", revoked_at=revoked_at, revocation_reason=revocation_reason
    )

    # Then: the session is stored with that reason.
    assert _stored_value(connection, "sessions", session_id, "revocation_reason") == (
        revocation_reason
    )


@pytest.mark.parametrize(
    ("revoked_at", "revocation_reason"),
    [(NOW, None), (None, "signed_out")],
    ids=["revoked-without-reason", "reason-without-revocation"],
)
def test_a_session_rejects_a_revocation_reason_without_its_instant_or_the_reverse(
    connection: Connection, revoked_at: datetime | None, revocation_reason: str | None
) -> None:
    # Given: the migrated database.

    # When: a session is stored with only one of the revocation instant and reason.
    # Then: the database rejects it.
    with (
        pytest.raises(IntegrityError, match="ck_sessions_revocation_reason_with_revoked_at"),
        connection.begin_nested(),
    ):
        _insert(connection, "sessions", revoked_at=revoked_at, revocation_reason=revocation_reason)


VOCABULARIES: list[tuple[str, str, list[str], str, dict[str, object]]] = [
    ("users", "role", ["user", "admin"], "owner", {}),
    ("external_identities", "provider", ["google"], "apple", {}),
    ("sessions", "sign_in_method", ["password", "google"], "apple", {}),
    ("sessions", "client_kind", ["web", "ios", "android"], "desktop", {}),
    (
        "sessions",
        "revocation_reason",
        [
            "signed_out",
            "revoked_by_user",
            "password_changed",
            "refresh_token_reused",
            "account_suspended",
            "account_deleted",
        ],
        "expired",
        {"revoked_at": NOW},
    ),
    (
        "email_challenges",
        "purpose",
        ["verify_email", "reset_password", "change_email"],
        "magic_link",
        {},
    ),
    ("oauth_authorization_attempts", "provider", ["google"], "apple", {}),
    (
        "oauth_authorization_attempts",
        "purpose",
        ["sign_in", "link", "reauthenticate"],
        "sign_up",
        {},
    ),
    ("oauth_authorization_attempts", "client_kind", ["web", "ios", "android"], "desktop", {}),
]
"""Each closed vocabulary from the ERD, with a realistic value outside it.

An entry holds the table, the column, its values, a realistic value the ERD
leaves out, and any column the row needs alongside it.
"""


@pytest.mark.parametrize(
    ("table_name", "column", "value", "companions"),
    [
        (table_name, column, value, companions)
        for table_name, column, values, _, companions in VOCABULARIES
        for value in values
    ],
)
def test_a_closed_vocabulary_accepts_each_of_its_values(
    connection: Connection,
    table_name: str,
    column: str,
    value: str,
    companions: dict[str, object],
) -> None:
    # Given: the migrated database.

    # When: a row is stored with one of the column's values.
    row_id = _insert(connection, table_name, **companions, **{column: value})

    # Then: the row is stored with that value.
    assert _stored_value(connection, table_name, row_id, column) == value


@pytest.mark.parametrize(
    ("table_name", "column", "rejected_value", "companions"),
    [
        (table_name, column, rejected_value, companions)
        for table_name, column, _, rejected_value, companions in VOCABULARIES
    ],
)
def test_a_closed_vocabulary_rejects_a_value_outside_it(
    connection: Connection,
    table_name: str,
    column: str,
    rejected_value: str,
    companions: dict[str, object],
) -> None:
    # Given: the migrated database.

    # When: a row is stored with a realistic value the vocabulary leaves out.
    # Then: the database rejects it through the column's check constraint.
    with (
        pytest.raises(IntegrityError, match=f"ck_{table_name}_{column}_vocabulary"),
        connection.begin_nested(),
    ):
        _insert(connection, table_name, **companions, **{column: rejected_value})


def test_a_second_unconsumed_challenge_for_the_same_purpose_is_rejected(
    connection: Connection,
) -> None:
    # Given: a user with an unconsumed verification code.
    user_id = _insert(connection, "users")
    _insert(connection, "email_challenges", user_id=user_id, purpose="verify_email")

    # When: a second unconsumed code for the same purpose is stored.
    # Then: the database rejects it, so at most one code per purpose works.
    with (
        pytest.raises(IntegrityError, match="uq_email_challenges_unconsumed_user_id_purpose"),
        connection.begin_nested(),
    ):
        _insert(connection, "email_challenges", user_id=user_id, purpose="verify_email")


def test_a_new_challenge_is_accepted_once_the_previous_one_is_consumed(
    connection: Connection,
) -> None:
    # Given: a user whose verification code was consumed.
    user_id = _insert(connection, "users")
    _insert(
        connection, "email_challenges", user_id=user_id, purpose="verify_email", consumed_at=NOW
    )

    # When: a new code for the same purpose is stored.
    _insert(connection, "email_challenges", user_id=user_id, purpose="verify_email")

    # Then: the user has both the consumed and the new code.
    assert _count(connection, "email_challenges") == 2
