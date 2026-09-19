"""Fixtures shared by the integration tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from job_status_found.app.app import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Run a fresh application through its lifespan, without following redirects."""
    with TestClient(create_app(), follow_redirects=False) as test_client:
        yield test_client
