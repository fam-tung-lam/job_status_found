"""Fixtures shared by the integration tests."""

import json
import re
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine, text
from sqlalchemy.pool import NullPool

from job_status_found.app.app import create_app
from job_status_found.features.auth.auth_settings import get_auth_settings
from job_status_found.features.core import AppSettings, get_app_settings

_TEST_DATABASE_NAME_PATTERN = re.compile(r"jsf_test_[0-9a-f]{32}")
"""The only database names this test harness may create or drop."""

_TEST_AUTH_KEY = "integration-suite-auth-key-with-at-least-32-characters"
"""The non-production HMAC and JWT key configured for integration application startup."""


@pytest.fixture(autouse=True)
def auth_application_configured(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Give every integration app the required non-production auth secrets."""
    monkeypatch.setenv("JSF_AUTH_HMAC_KEY", _TEST_AUTH_KEY)
    monkeypatch.setenv("JSF_AUTH_JWT_SIGNING_KEY_ID", "integration-1")
    monkeypatch.setenv("JSF_AUTH_JWT_KEY_RING", json.dumps({"integration-1": _TEST_AUTH_KEY}))
    get_auth_settings.cache_clear()
    yield
    get_auth_settings.cache_clear()


def _require_disposable_database_name(database_name: str) -> None:
    """Refuse a database name that the integration harness does not own."""
    if _TEST_DATABASE_NAME_PATTERN.fullmatch(database_name) is None:
        error_message = f"Refusing unsafe integration-test database name: {database_name!r}."
        raise RuntimeError(error_message)


def _upgrade_database_to_head(database_url: URL, project_root: Path) -> None:
    """Apply every Alembic revision to a disposable test database."""
    database_engine = create_engine(database_url, poolclass=NullPool)
    try:
        with database_engine.begin() as connection:
            current_database = connection.scalar(text("SELECT current_database()"))
            if current_database != database_url.database:
                error_message = (
                    f"Connected to {current_database!r}, expected disposable database "
                    f"{database_url.database!r}."
                )
                raise RuntimeError(error_message)
            config = Config(
                str(project_root / "alembic.ini"), attributes={"connection": connection}
            )
            command.upgrade(config, "head")
    finally:
        database_engine.dispose()


@contextmanager
def _empty_test_database() -> Iterator[URL]:
    """Create and finally drop one empty disposable PostgreSQL database."""
    server_url = AppSettings().database_url.set(database="postgres")
    database_name = f"jsf_test_{uuid4().hex}"
    _require_disposable_database_name(database_name)
    admin_engine = create_engine(server_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        try:
            yield server_url.set(database=database_name)
        finally:
            _require_disposable_database_name(database_name)
            with admin_engine.connect() as connection:
                connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def create_test_database() -> Callable[[], AbstractContextManager[URL]]:
    """Provide the shared factory for empty disposable PostgreSQL databases."""
    return _empty_test_database


@pytest.fixture(scope="session")
def test_database_name(
    pytestconfig: pytest.Config,
    create_test_database: Callable[[], AbstractContextManager[URL]],
) -> Iterator[str]:
    """Provide one migrated disposable database for API and SQL-adapter tests."""
    with create_test_database() as database_url:
        _upgrade_database_to_head(database_url, pytestconfig.rootpath)
        database_name = database_url.database
        if database_name is None:
            raise RuntimeError("The disposable integration-test URL has no database name.")
        _require_disposable_database_name(database_name)
        yield database_name


@pytest.fixture
def test_database_configured(
    test_database_name: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """Point application settings at the disposable integration-test database."""
    _require_disposable_database_name(test_database_name)
    monkeypatch.setenv("JSF_DATABASE_NAME", test_database_name)
    get_app_settings.cache_clear()
    assert get_app_settings().database_name == test_database_name
    yield
    get_app_settings.cache_clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Run a fresh application through its lifespan, without following redirects."""
    with TestClient(create_app(), follow_redirects=False) as test_client:
        yield test_client
