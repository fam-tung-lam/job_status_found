# Python and FastAPI Testing

Pytest expression, fixture, patching, and cleanup mechanics, then ASGI test
mechanics for an assembled FastAPI application. Use the repository's existing
runner when it is not pytest.

## Express the behavior

- Use plain assertions and let pytest show the value diff.
- Use `pytest.raises` with the exact type and `match=` for a stable promised
  message. Use `pytest.warns` for a promised warning.
- Parameterize cases that exercise one rule with different inputs. Split cases
  that need different setup, action, or outcome.

## Own setup and cleanup

Keep one-test setup in the test. Promote repeated setup to the narrowest fixture
scope that holds its real consumers. A fixture that acquires a resource uses
`yield` and releases it after the yield, including when the test body fails.
Register cleanup right after each successful acquisition with a context manager,
`ExitStack`, or a finalizer, so a failure before `yield` cannot leak an earlier
resource.

Read the installed async pytest plugin and its configured mode before adding a
marker. Do not add a redundant async marker when automatic mode already owns
collection.

Use `monkeypatch` or a spec-constrained mock at an external boundary. Patch the
name where the code under test looks it up. Use `AsyncMock` only for an awaited
contract, and keep one-off patches in the test that needs them.

Use pytest fixtures such as `tmp_path`, `monkeypatch`, `capsys`, and `caplog`
for controlled boundaries instead of shared mutable test globals.

The
[pytest fixture guide](https://docs.pytest.org/en/stable/how-to/fixtures.html)
identifies the feature; it is not required reading. When fixture behavior
differs, read the installed package and prove acquisition and cleanup with a
focused test.

## Test through the HTTP boundary

Exercise the assembled application through its HTTP boundary. Assert the exact
status, response body, important headers, authentication result, and any
database or job effect an outsider can observe. Keep service and repository edge
cases at their cheaper Python test level.

## Mirror capability ownership

In the default layout, put use-case tests under
`tests/features/<feature>/unit/application/use_cases/`, domain tests under
`tests/features/<feature>/unit/domain/`, and real adapter or presentation
collaboration tests under the matching layer in
`tests/features/<feature>/integration/`. Name a router test
`test_<resource>_controller.py` after its module, as
[file-organization.md](file-organization.md) requires. Put fixtures owned by one
feature in that feature's `conftest.py`.

Put tests of the assembled app, including lifespan, under `tests/app/`. Keep a
reusable test double at the nearest common feature and level. Use pytest markers
for suite selection when the repository configures them; markers do not replace
the ownership the tree expresses.

Placement is the only architecture rule here. The behavior contract owns what
each level proves. Keep a coherent existing test root and leave unrelated tests
in place.

## Select the client

- Use `TestClient` as a context manager for synchronous pytest tests so the
  lifespan runs.
- Use the repository's async ASGI client and transport when the test must await
  other async collaborators. HTTPX names and compatibility belong to the
  installed FastAPI and Starlette versions. Arrange the lifespan explicitly,
  because a bare transport may not start it.
- Disable redirect following when testing a canonical path or trailing-slash
  policy.
- Leave application-exception propagation on for ordinary tests. Only when
  asserting the outer 500 envelope, use `raise_server_exceptions=False` on
  `TestClient` or the transport's `raise_app_exceptions=False` equivalent.

The [async test](https://fastapi.tiangolo.com/advanced/async-tests/) and
[lifespan test](https://fastapi.tiangolo.com/advanced/testing-events/) links
identify the features; they are not required reading. When client or lifespan
behavior differs, read the locked packages and prove startup, request, and
shutdown behavior with a focused local test.

## Isolate request dependencies

Override the exact dependency callable stored in `app.dependency_overrides`.
Install the override in a fixture. In `finally`, restore that key's previous
value or delete only that key, so the test keeps overrides it did not own.

Keep the assembled controller, validation, dependency graph, exception handlers,
and middleware real. Replace external effects only through the chosen dependency
or application seam.

Cover success, malformed and boundary input, missing authentication, denied
authorization, mapped domain failure, and unexpected external failure when the
change can produce them. For a queued operation, assert the durable handoff and
payload instead of running the worker inside every endpoint test.

Inspect `app.openapi()` or its served document when a public operation changes.
Assert the affected path, schema, security requirement, and status without
snapshotting unrelated generated output.

Finish when the focused test fails for the broken behavior and passes for the
implemented contract, an HTTP test would fail for a broken HTTP contract, every
override and resource is cleaned up so no state reaches the next test, and no
uncontrolled service is left running.
