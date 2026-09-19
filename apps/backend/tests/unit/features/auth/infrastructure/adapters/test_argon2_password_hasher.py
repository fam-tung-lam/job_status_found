import anyio
from anyio import CapacityLimiter

from job_status_found.features.auth.infrastructure.adapters.argon2_password_hasher import (
    Argon2PasswordHasher,
)


async def test_the_event_loop_keeps_serving_while_a_password_hashes() -> None:
    # Given: a hasher, and a task that counts event-loop turns.
    hasher = Argon2PasswordHasher(CapacityLimiter(1))
    turns = 0
    hashed = anyio.Event()

    async def count_turns() -> None:
        nonlocal turns
        while not hashed.is_set():
            turns += 1
            await anyio.sleep(0.001)

    # When: a password hashes beside that task.
    async with anyio.create_task_group() as task_group:
        task_group.start_soon(count_turns)
        await hasher.hash("a password to hash")
        hashed.set()

    # Then: the loop turned many times during the tens of milliseconds a hash
    # takes, so the hash ran off the loop.
    assert turns > 5


async def test_hashes_beyond_the_limit_wait_for_a_free_slot() -> None:
    # Given: a hasher limited to one hash at a time.
    limiter = CapacityLimiter(1)
    hasher = Argon2PasswordHasher(limiter)

    # When: two passwords hash at once.
    waiting_while_hashing = 0
    async with anyio.create_task_group() as task_group:
        task_group.start_soon(hasher.hash, "first password")
        task_group.start_soon(hasher.hash, "second password")
        await anyio.sleep(0.005)
        waiting_while_hashing = limiter.statistics().tasks_waiting

    # Then: the second waited while the first hashed.
    assert waiting_while_hashing == 1
