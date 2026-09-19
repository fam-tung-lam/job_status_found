"""Unit tests of how `hash_password` runs hashes beside the event loop."""

from functools import partial
from threading import Event

import anyio
import pytest
from anyio import CapacityLimiter
from pytest_mock import MockerFixture

import job_status_found.features.auth.infrastructure.helpers.hash_password as hash_password_module
from job_status_found.features.auth.infrastructure.helpers.hash_password import hash_password


async def _wait_until_event_is_set(event: anyio.Event) -> None:
    """Wait for an AnyIO signal with a bounded failure time."""
    with anyio.fail_after(5):
        await event.wait()


class TestHashPassword:
    """Where `hash_password` runs a hash, and how many it runs at once."""

    @pytest.mark.asyncio
    async def test_the_event_loop_keeps_serving_while_a_password_hashes(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: a hash blocked in its worker thread.
        When: the event loop observes it before releasing it.
        Then: the event loop remained available while the hash was blocked.
        """
        # Given: a hash that signals its worker thread and waits for release.
        limiter = CapacityLimiter(1)
        hash_started = anyio.Event()
        release_hash = Event()
        password_hasher = mocker.patch.object(
            hash_password_module, "_ARGON2ID_PASSWORD_HASHER", autospec=True
        )

        def hash_after_release(password: str) -> str:
            """Block the worker thread until the test releases the hash."""
            anyio.from_thread.run_sync(hash_started.set)
            if not release_hash.wait(timeout=5):
                raise TimeoutError("The test did not release the password hash.")
            return f"hashed:{password}"

        password_hasher.hash.side_effect = hash_after_release
        hashes: list[str] = []

        async def hash_and_store_result() -> None:
            """Hash one password and retain its result for the assertion."""
            hashes.append(await hash_password("a password to hash", limiter=limiter))

        # When: the hash blocks in its worker thread and the event loop observes it.
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(hash_and_store_result)
            try:
                await _wait_until_event_is_set(hash_started)

                # Then: the event loop is running while the worker remains blocked.
                assert hashes == []
            finally:
                release_hash.set()

        assert hashes == ["hashed:a password to hash"]

    @pytest.mark.asyncio
    async def test_hashes_beyond_the_limit_wait_for_a_free_slot(
        self, mocker: MockerFixture
    ) -> None:
        """
        Given: a limiter that admits one hash at a time.
        When: two passwords hash at once.
        Then: the second hash waits while the first one runs.
        """
        # Given: a limiter that admits one hash at a time, and a first hash that
        # waits for the test to release it.
        limiter = CapacityLimiter(1)
        hash_password_under_limit = partial(hash_password, limiter=limiter)
        first_hash_started = anyio.Event()
        second_hash_started = anyio.Event()
        release_first_hash = Event()
        password_hasher = mocker.patch.object(
            hash_password_module, "_ARGON2ID_PASSWORD_HASHER", autospec=True
        )

        def hash_with_first_call_blocked(password: str) -> str:
            """Block the first hash and signal when the second enters the worker."""
            if not first_hash_started.is_set():
                anyio.from_thread.run_sync(first_hash_started.set)
                if not release_first_hash.wait(timeout=5):
                    raise TimeoutError("The test did not release the first password hash.")
            else:
                anyio.from_thread.run_sync(second_hash_started.set)
            return f"hashed:{password}"

        password_hasher.hash.side_effect = hash_with_first_call_blocked

        # When: two passwords hash at once.
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(hash_password_under_limit, "first password")
            task_group.start_soon(hash_password_under_limit, "second password")
            try:
                await _wait_until_event_is_set(first_hash_started)
                await anyio.wait_all_tasks_blocked()

                # Then: the queued hash has not entered a worker before release.
                assert limiter.statistics().tasks_waiting == 1
                assert not second_hash_started.is_set()
            finally:
                release_first_hash.set()
            await _wait_until_event_is_set(second_hash_started)
