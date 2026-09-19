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
from job_status_found.features.core import get_app_settings

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The instant every registration in these tests happens."""


@pytest.fixture
async def database_engine() -> AsyncIterator[AsyncEngine]:
    """Connect to the application's database for the length of one test."""
    database_engine = create_async_engine(get_app_settings().database_url)
    yield database_engine
    await database_engine.dispose()


@pytest.fixture
async def unique_address(database_engine: AsyncEngine) -> AsyncIterator[str]:
    """Hand out a unique address, and delete its account afterwards."""
    unique_address = f"race.{uuid4().hex}@example.com"
    yield unique_address
    async with database_engine.begin() as connection:
        await connection.execute(
            delete(UserTable).where(UserTable.email_normalized == unique_address)
        )


async def _wait_until_blocked(database_engine: AsyncEngine, backend_pid: int) -> None:
    """Wait until the database backend with a PID waits for another transaction's lock."""
    with anyio.fail_after(5):
        while True:
            # A new connection per check, so no transaction snapshot hides the change.
            async with database_engine.connect() as connection:
                is_blocked = await connection.scalar(
                    text("SELECT cardinality(pg_blocking_pids(:pid)) > 0"), {"pid": backend_pid}
                )
            if is_blocked:
                return
            await anyio.sleep(0.01)


async def test_two_concurrent_sign_ups_create_one_account_without_an_error(
    database_engine: AsyncEngine, unique_address: str
) -> None:
    # Given: one transaction has created an account for the email but not
    # yet committed.
    registration = UserRegistration(
        email=EmailAddress(unique_address),
        first_name="Jane",
        last_name="Doe",
        registered_at=NOW,
    )
    async with (
        AsyncSession(database_engine) as first_session,
        AsyncSession(database_engine) as second_session,
    ):
        first_created_user = await SqlUserRepository(
            first_session
        ).create_unverified_user_unless_email_taken(registration)
        second_backend_pid = await second_session.scalar(text("SELECT pg_backend_pid()"))
        assert isinstance(second_backend_pid, int)
        second_transaction_results: list[User | None] = []

        async def create_in_second_transaction() -> None:
            """Create the same account in the second transaction and keep the result."""
            second_transaction_results.append(
                await SqlUserRepository(second_session).create_unverified_user_unless_email_taken(
                    registration
                )
            )

        # When: a second transaction creates an account for the same email,
        # and the first commits while the second waits for it.
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(create_in_second_transaction)
            await _wait_until_blocked(database_engine, second_backend_pid)
            await first_session.commit()

    # Then: the first created the account, and the second learned it exists
    # instead of failing on the unique email.
    assert first_created_user is not None
    assert second_transaction_results == [None]
