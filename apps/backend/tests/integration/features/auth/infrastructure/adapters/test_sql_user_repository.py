"""Integration tests of `SqlUserRepository` against PostgreSQL."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import anyio
import pytest
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from job_status_found.features.auth.application.dtos.user_registration import UserRegistration
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.infrastructure.adapters.sql_user_repository import (
    SqlUserRepository,
)
from job_status_found.features.auth.infrastructure.db.tables import UserTable
from job_status_found.features.core import get_settings

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The instant every registration in these tests happens."""


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """Connect to the application's database for the length of one test."""
    engine = create_async_engine(get_settings().database_url)
    yield engine
    await engine.dispose()


@pytest.fixture
async def address(engine: AsyncEngine) -> AsyncIterator[str]:
    """Hand out a unique address, and delete its account afterwards."""
    address = f"race.{uuid4().hex}@example.com"
    yield address
    async with engine.begin() as connection:
        await connection.execute(delete(UserTable).where(UserTable.email_normalized == address))


async def _wait_until_blocked(engine: AsyncEngine, backend_pid: int) -> None:
    """Wait until the database backend with a PID waits for another transaction's lock."""
    with anyio.fail_after(5):
        while True:
            # A new connection per check, so no transaction snapshot hides the change.
            async with engine.connect() as connection:
                blocked = await connection.scalar(
                    text("SELECT cardinality(pg_blocking_pids(:pid)) > 0"), {"pid": backend_pid}
                )
            if blocked:
                return
            await anyio.sleep(0.01)


async def test_two_concurrent_sign_ups_create_one_account_without_an_error(
    engine: AsyncEngine, address: str
) -> None:
    # Given: one transaction has created an account for the email but not
    # yet committed.
    registration = UserRegistration(
        email=EmailAddress(address),
        first_name="Jane",
        last_name="Doe",
        terms_version="2026-09-18",
        registered_at=NOW,
    )
    async with AsyncSession(engine) as first, AsyncSession(engine) as second:
        created = await SqlUserRepository(first).add_unverified(registration)
        second_backend_pid = await second.scalar(text("SELECT pg_backend_pid()"))
        assert isinstance(second_backend_pid, int)
        outcome: list[User | None] = []

        async def add_in_second_transaction() -> None:
            """Create the same account in the second transaction and keep the result."""
            outcome.append(await SqlUserRepository(second).add_unverified(registration))

        # When: a second transaction creates an account for the same email,
        # and the first commits while the second waits for it.
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(add_in_second_transaction)
            await _wait_until_blocked(engine, second_backend_pid)
            await first.commit()

    # Then: the first created the account, and the second learned it exists
    # instead of failing on the unique email.
    assert created is not None
    assert outcome == [None]
