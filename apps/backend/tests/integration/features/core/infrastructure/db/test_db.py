"""Integration tests of the database lifespan and request session against PostgreSQL."""

from collections.abc import Iterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.app.app import create_app
from job_status_found.features.core import get_app_settings, get_database_session


@pytest.fixture
def postgres_database_configured(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Name the server's `postgres` database in the settings, and drop the cached ones around.

    The default database name and `.env` both say `job_status_found`, so only
    another name proves the setting is used.
    """
    monkeypatch.setenv("JSF_DATABASE_NAME", "postgres")
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


@pytest.fixture
def unreachable_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Point the settings at a port where no database listens, and drop the cached ones around."""
    monkeypatch.setenv("JSF_DATABASE_HOST", "127.0.0.1")
    monkeypatch.setenv("JSF_DATABASE_PORT", "1")
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


def _create_app_reporting_its_database_name() -> FastAPI:
    """Build the app plus a route that reports which database its request session uses."""
    app = create_app()

    @app.get("/database-name")
    async def read_database_name(
        session: Annotated[AsyncSession, Depends(get_database_session)],
    ) -> str:
        """Report the name of the database the request session is connected to."""
        return str(await session.scalar(text("SELECT current_database()")))

    return app


class TestGetDatabaseSession:
    """The request session `get_database_session` provides to a route."""

    @pytest.mark.usefixtures("postgres_database_configured")
    def test_a_request_session_reaches_the_configured_database(self) -> None:
        """
        Given: settings that name the server's `postgres` database.
        When: a route that uses a request session is called while the application runs.
        Then: the session answers from the database the settings name.
        """
        # Given: settings that name the server's `postgres` database, and a route
        # that uses a request session.
        app = _create_app_reporting_its_database_name()

        # When: the route is called while the application runs.
        with TestClient(app) as client:
            response = client.get("/database-name")

        # Then: the session answered from the database the settings name.
        assert response.status_code == 200
        assert response.json() == "postgres"

    def test_a_request_session_fails_clearly_when_no_lifespan_opened_the_database(self) -> None:
        """
        Given: an application whose lifespan never ran.
        When: a route that needs a request session is called.
        Then: the request fails with an error that names the missing lifespan.
        """
        # Given: an application whose lifespan never ran, so no database is open.
        client = TestClient(_create_app_reporting_its_database_name())

        # When: a route that needs a session is called.
        # Then: the request fails with a message that names the missing lifespan.
        with pytest.raises(RuntimeError, match="lifespan opens it"):
            client.get("/database-name")


class TestOpenDatabase:
    """The database lifespan `open_database` that the application starts with."""

    @pytest.mark.usefixtures("unreachable_database")
    def test_the_application_starts_and_reports_health_without_a_reachable_database(
        self,
    ) -> None:
        """
        Given: settings that point at a port where no database listens.
        When: the application starts and the health endpoint is called.
        Then: the health endpoint answers, because liveness does not need the database.
        """
        # Given: settings that point at a port where no database listens.
        app = create_app()

        # When: the application starts and the health endpoint is called.
        with TestClient(app) as client:
            response = client.get("/health")

        # Then: liveness does not depend on the database.
        assert response.status_code == 200
