from collections.abc import Iterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.app.app import create_app
from job_status_found.app.app_settings import get_settings
from job_status_found.db.db import get_database_session


# The default database name and `.env` both say `job_status_found`, so the test
# points at the server's `postgres` database to prove the setting is used.
@pytest.fixture
def postgres_database_configured(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("JSF_DATABASE_NAME", "postgres")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def unreachable_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("JSF_DATABASE_HOST", "127.0.0.1")
    monkeypatch.setenv("JSF_DATABASE_PORT", "1")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# The application plus a route that asks its request session which database it uses.
def _create_app_reporting_its_database_name() -> FastAPI:
    app = create_app()

    @app.get("/database-name")
    async def read_database_name(
        session: Annotated[AsyncSession, Depends(get_database_session)],
    ) -> str:
        return str(await session.scalar(text("SELECT current_database()")))

    return app


@pytest.mark.usefixtures("postgres_database_configured")
def test_a_request_session_reaches_the_configured_database() -> None:
    # Given: settings that name the server's `postgres` database, and a route
    # that uses a request session.
    app = _create_app_reporting_its_database_name()

    # When: the route is called while the application runs.
    with TestClient(app) as client:
        response = client.get("/database-name")

    # Then: the session answered from the database the settings name.
    assert response.status_code == 200
    assert response.json() == "postgres"


def test_a_request_session_fails_clearly_when_no_lifespan_opened_the_database() -> None:
    # Given: an application whose lifespan never ran, so no database is open.
    client = TestClient(_create_app_reporting_its_database_name())

    # When: a route that needs a session is called.
    # Then: the request fails with a message that names the missing lifespan.
    with pytest.raises(RuntimeError, match="lifespan opens it"):
        client.get("/database-name")


@pytest.mark.usefixtures("unreachable_database")
def test_the_application_starts_and_reports_health_without_a_reachable_database() -> None:
    # Given: settings that point at a port where no database listens.
    app = create_app()

    # When: the application starts and the health endpoint is called.
    with TestClient(app) as client:
        response = client.get("/health")

    # Then: liveness does not depend on the database.
    assert response.status_code == 200
