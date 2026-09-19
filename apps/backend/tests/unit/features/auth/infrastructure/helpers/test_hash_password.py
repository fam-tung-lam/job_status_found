"""Unit tests of how `hash_password` runs hashes beside the event loop."""

from functools import partial

import anyio
from anyio import CapacityLimiter

from job_status_found.features.auth.infrastructure.helpers.hash_password import hash_password


async def test_the_event_loop_keeps_serving_while_a_password_hashes() -> None:
    # Given: a limiter, and a task that counts event-loop turns.
    limiter = CapacityLimiter(1)
    event_loop_turns = 0
    hash_finished = anyio.Event()

    async def count_turns() -> None:
        """Count event-loop turns until the hash is done."""
        nonlocal event_loop_turns
        while not hash_finished.is_set():
            event_loop_turns += 1
            await anyio.sleep(0.001)

    # When: a password hashes beside that task.
    async with anyio.create_task_group() as task_group:
        task_group.start_soon(count_turns)
        await hash_password("a password to hash", limiter=limiter)
        hash_finished.set()

    # Then: the loop turned many times during the tens of milliseconds a hash
    # takes, so the hash ran off the loop.
    assert event_loop_turns > 5


async def test_hashes_beyond_the_limit_wait_for_a_free_slot() -> None:
    # Given: a limiter that admits one hash at a time.
    limiter = CapacityLimiter(1)
    hash_password_under_limit = partial(hash_password, limiter=limiter)

    # When: two passwords hash at once.
    waiting_while_hashing = 0
    async with anyio.create_task_group() as task_group:
        task_group.start_soon(hash_password_under_limit, "first password")
        task_group.start_soon(hash_password_under_limit, "second password")
        await anyio.sleep(0.005)
        waiting_while_hashing = limiter.statistics().tasks_waiting

    # Then: the second waited while the first hashed.
    assert waiting_while_hashing == 1
