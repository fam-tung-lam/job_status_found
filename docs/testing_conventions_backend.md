# Backend testing conventions

Keep the unit/integration split. Test decisions in isolation and persistence,
delivery, and framework behavior through real components. This file is
authoritative for backend testing and takes precedence over `AGENTS.md` when
testing rules conflict.

## Structure and documentation

- Tests live in `tests/{unit,integration}/`, followed by the source path, in
  `test_<module>.py`. Migration tests mirror paths under `migrations/`.
- pytest uses `--import-mode=importlib`, so unit and integration modules may
  share a name. Never import one test module from another. Put shared fixtures
  in the nearest `conftest.py` that contains all users.
- Every test is a method of a `Test<Subject>` class. A module may use one class
  per subject or per distinct risk. Fixtures, helpers, and constants stay at
  module level unless a mock-based class's `_set_up` owns them.
- Every test declaration has a docstring. A test class names its subject. A
  test method's multiline docstring states `Given:`, `When:`, and `Then:`, plus
  `And:` where needed. Test helpers use concise one-line docstrings.
- Test bodies retain explicit Given-When-Then comments. These rules also apply
  to private declarations because Ruff ignores `D` and `DOC` in tests.
- Mark every async test with `@pytest.mark.asyncio`, below `parametrize`. Pass
  effect-only fixtures through `@pytest.mark.usefixtures`.

## Choose the level

Keep `tests/{unit,integration}/<source path>/test_<module>.py`,
`Test<Subject>` classes, Given-When-Then comments, and existing docstring rules.

| Subject | Level | Dependencies |
| --- | --- | --- |
| Domain rules and custom request/settings validators | Unit | Real logic; controlled environment |
| Use-case decisions and required side effects | Unit | Real domain rules; autospecced ports and injected helper stubs |
| Local library wrappers | Unit | Real library; patch only a specific error or scheduling path |
| SQL queries, locks, conflicts, and atomicity | Integration | Real PostgreSQL |
| Endpoint contracts, persistence, and delivery | Integration | Fresh app and the real services the path needs |
| Migrations, lifespan, CORS, and app assembly | Integration | Relevant real database/framework components |

Unit tests must run without Docker, network services, or developer credentials.
Keep infrastructure fixtures under `tests/integration/`. An HTTP test remains
an integration test even when its path needs no database or mail server.

## Test behavior once

- Name the defect each test catches. Prove it at the cheapest sufficient level.
- Cover decision boundaries in unit tests and assembly/persisted effects in
  integration tests. A domain refusal and its HTTP mapping are different risks;
  repeating the same decision matrix at both levels is duplication.
- Assert expected state, typed failures, required absence, or meaningful effects.
  Avoid presence-only assertions and checks that merely repeat declarations.
- Assert contractual values and bounds, not random hashes, incidental headers,
  or exact elapsed durations.
- Add regression tests for fixed defects unless existing tests or static checks
  already cover the risk. Do not test framework behavior or plain CRUD twice.

## Keep mocks narrow

Use pytest-mock: autospecs for ports, stubs for injected helpers, and
`mocker.patch.object(..., autospec=True)` where the library call is looked up.
Keep mocks per test, visible in the test or its class's `_set_up`.

Do not import `unittest.mock`, write fake classes, use patch decorators/context
managers, or use class/session-scoped mocks. A mock-based class creates fresh
doubles and its subject in an autouse `_set_up` fixture. Use `mocker.Mock()` and
`mocker.call` for recorders and matchers. Let pytest-mock perform teardown.

Repository doubles are valid for isolated use-case decisions. They do not prove
SQL behavior or durability. Prefer state assertions; assert call counts or order
only when changing them would cause a defect, such as emailing before commit.
Do not assert incidental reads or complete internal call sequences.

Integration tests keep real PostgreSQL, Mailpit, hashing, HMAC, and token
verification. Replace unavailable third-party network boundaries, not the
application behavior being tested. Never install suite-wide service or security
mocks. Introduce cheaper hashing parameters only after measuring a need, retaining
production-cost interoperability coverage.

## Exercise FastAPI correctly

- Use a fresh `create_app()` inside
  `with TestClient(app, follow_redirects=False)` so lifespan runs.
- Keep exception propagation enabled unless inspecting an unhandled 500 response.
- Override dependencies through that app's `dependency_overrides`. Limit overrides
  to explicit boundaries such as time or third-party transport; restore them if
  the app outlives the fixture.
- Set environment variables before app creation. Clear cached settings before
  and after tests. Direct settings tests use `_env_file=None`.
- Keep explicit `@pytest.mark.asyncio` and compatible fixture/loop scopes.
  Do not share async sessions across `TestClient`'s loop and the test's loop.
- If same-loop async HTTP tests become necessary, explicitly extend the current
  `TestClient` convention: use `httpx2.AsyncClient`, `ASGITransport`, and managed
  lifespan. The async client alone does not start lifespan.

For each endpoint, cover success and required effects, documented failure
mappings, and representative request validation. Add authentication and
cross-owner authorization cases when applicable. Test shared error-envelope
behavior once; route tests prove they reach the correct mapping.

Test security through behavior: CORS, applicable cookie flags and expiry rules,
unsafe settings rejection, and secret-free responses, redirects, and logs.
Compare promised responses across account states to detect enumeration.
A minimum-duration assertion alone does not prove timing-attack resistance.

For OAuth, keep real signature and claim verification with synthetic test keys.
Replace provider transport with controlled token/JWKS responses and verify the
outgoing request. Offline tests cannot validate live provider configuration.

## Isolate databases and clean up

Use an explicitly configured test database, such as `job_status_found_test`, or
a disposable database per run/worker. Never fall back to the development database.
Validate the target before writes or cleanup and confirm `current_database()`.
Use a dedicated test server/role; a database-name suffix alone is insufficient.

Build schemas through Alembic on the project's PostgreSQL version. Missing
required services must fail the integration run rather than silently skip it.

- Single-connection adapter tests can roll back an outer transaction.
  `join_transaction_mode="create_savepoint"` also permits session commits, but
  does not prove durable commits or visibility to independent connections.
- API and concurrency tests use real commits, independent sessions where needed,
  unique rows, and targeted cleanup. Synchronize races explicitly; do not assume
  a sleep establishes lock contention.
- Migration tests use throwaway databases with administrative privileges confined
  to test infrastructure.
- Delete only the test's rows and messages, including surviving audit records.
  Check cleanup responses and attempt remaining cleanup if one resource fails.
  Isolate shared resources before enabling parallel workers.

## Keep fixtures and assertions deterministic

Prefer small `yield` fixtures. Register cleanup after successful acquisition when
later setup can fail; teardown after `yield` does not run if setup never reaches
it. Close clients, dispose engines, and restore caches after failures.

Keep builders local until another module needs them, then share through the
nearest `conftest.py`. Do not import test modules into one another.

Control business time at decision boundaries. Use monotonic deadlines, bounded
polling, and request timeouts for real delivery or lock state. Use explicit
entry/release events for scheduling tests instead of machine-speed assumptions.

Never require independent random codes to differ. Compare the delivered code's
hash with storage and verify salted password hashes with the real verifier.
Do not hide flaky tests with retries. Temporary skips or strict `xfail` marks
need a tracked reason and re-enable condition; remove placeholder tests.

## Cover data and compatibility risks

- Parametrize custom validation and parsing with boundary inputs and sanitized,
  realistic payloads. Add property-based tests only for uncovered invariants.
- Add consistency checks only when independent sources must agree and no existing
  tool compares them.
- Test old wire/stored values after a rename only when compatibility is promised.
  Otherwise test the intended migration or rejection.
- Test data fixes on affected and preserved rows, plus reruns and rollback when
  those guarantees apply.
- Test migrations from empty, the supported downgrade path, and upgrades of
  representative existing data. Prove constraints through actual writes/deletes.
  Use `alembic check` for detectable drift; it does not prove data preservation
  or every constraint expression.

A revision test uses a throwaway PostgreSQL database. It checks upgrade from
empty, downgrade to base, drift from mapped tables, and behavior PostgreSQL
enforces, including constraints, foreign-key actions, and partial indexes. Do
not restate the ERD or inspect metadata when `alembic check` owns the risk.

## Checks

From `apps/backend/`, use the committed lockfile:

```shell
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check
uv run --locked pytest tests/unit
```

Start PostgreSQL and Mailpit before checks that need them. See the backend README
when ports 5432, 1025, or 8025 are occupied.

Start the Compose services, then run the full suite:

```shell
docker compose up --wait postgres mailpit
uv run --locked pytest --cov
```

The integration harness creates, migrates, validates, and drops disposable
databases. Its configured PostgreSQL role therefore needs test-only permission to
create and drop databases. Migration tests run the Alembic drift check.

CI must run static checks, units without services, and isolated integration tests.
Keep branch measurement and the existing 90% full-suite coverage threshold.
Do not add declaration tests merely to raise coverage.

## Current review

Unit tests own send-interval decisions; API tests own persisted replacement.
Migration tests already use disposable databases. The integration harness creates
another disposable database for API and SQL-adapter tests and refuses an unsafe
name before creating or dropping it.

The remaining project-level gap is CI. Add static, service-free unit, and isolated
integration jobs before treating automated checks as a merge gate.
