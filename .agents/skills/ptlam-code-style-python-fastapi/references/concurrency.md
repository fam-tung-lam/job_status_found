# Python and FastAPI Concurrency

How Python code chooses synchronous or asynchronous execution and keeps
resources correct under concurrency, and how FastAPI picks a thread-pool path,
an event-loop path, a stream, or a durable handoff.

## Choose sync or async in Python

Use `async def` when the call path awaits non-blocking I/O. Keep a path
synchronous when its libraries are synchronous. An `async def` label does not
make a blocking database, network, filesystem, or subprocess call non-blocking.

Prefer the dependency's own async API. When none exists and the work is safe to
move to a thread, isolate it with `asyncio.to_thread` or the repository's
approved equivalent. Move CPU-bound work to the project's process or job
boundary rather than occupying the event loop or its thread pool.

## Keep concurrency structured

- Await work before leaving its owner. Use the project's task-group mechanism
  when sibling operations must share cancellation and failure.
- Never create an untracked background task inside a request or a library call.
  Give long-lived work a supervisor with an explicit shutdown path.
- Put timeouts at external boundaries, and tell a timeout apart from a caller's
  cancellation.
- Let cancellation travel on after cleanup. Never turn cancellation into an
  ordinary success or a retry.
- Do not share mutable clients, sessions, or buffers across concurrent tasks
  unless their contract says that is safe.

Acquire files, locks, sessions, streams, and clients with a context manager when
one exists; otherwise close them in `finally`. The error and cancellation paths
must release the same resources as the success path.

Test concurrency with observable readiness and controlled collaborators. Fixed
sleeps hide races and make the suite depend on machine speed.

## Choose the FastAPI dispatch path

Choose from the whole call graph:

| The path calls                                          | Handler or dependency                           |
| ------------------------------------------------------- | ----------------------------------------------- |
| Awaitable non-blocking I/O                              | `async def`, with every operation awaited       |
| A synchronous database, SDK, filesystem, or network API | `def`, so FastAPI may run it in its thread pool |
| CPU-heavy or durable work                               | A process or job system the repository owns     |

FastAPI runs ordinary `def` handlers and dependencies in a thread pool. It does
not move a synchronous helper called from your `async def`; that call blocks the
event loop. The [FastAPI async guide](https://fastapi.tiangolo.com/async/)
identifies the feature; it is not required reading. When dispatch behaves
differently, read the locked packages and prove the path with a focused local
test.

Never call a blocking synchronous API directly on the event loop. Prefer a plain
`def` handler for a synchronous call path. An approved thread offload is safe
only when the worker creates, uses, and closes its own thread-bound resource;
never pass a database session or another thread-bound client across threads or
tasks.

## Hand off background work

Use `BackgroundTasks` only for small in-process work whose loss on process exit
is acceptable. Hand durable, retryable, slow, or CPU-heavy work to the
repository's queue, and return the accepted-job response only after the handoff
succeeds.

Never let a background callback close over a yielded session, client, ORM
object, or request context. Pass stable data such as an identifier, then acquire
and close fresh resources inside the task.

A streaming response owns its iterator until disconnect or completion. Pass
cancellation on, close upstream streams, and keep yielded dependencies alive for
the response scope the installed FastAPI version requires.

Finish when no blocking call runs on an event loop, every spawned operation has
an owner, every job has a durability owner, and every acquired resource,
including a cancelled stream and its upstream, closes on all exits.
