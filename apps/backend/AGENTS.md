# Backend agent notes

## Docstrings

- Style: Google (`Args:`, `Returns:`, `Yields:`, `Raises:`, `Attributes:`,
  `Example:`). Do not mix NumPy or Sphinx field styles.
- Every module, package, class, function, method, and property has a
  docstring, public or private (`_name`), in `src/`, `migrations/`, and
  `tests/`. So does every module constant and class attribute: an attribute
  docstring on the line after it, such as `_SMTP_TIMEOUT_SECONDS`. A private
  docstring is concise: one sentence on what it does or holds, then the
  reason when the code does not show it.
- Instance attributes that `__init__` sets from its arguments are covered by
  its `Args:` section. Test functions are named for their behavior and carry
  Given-When-Then comments; test helpers take one-line docstrings without
  `Args:` or `Returns:` sections.
- Do not repeat types; annotations carry them.
- Property docstrings describe the value ("Whether...", "The..."), never start
  with a verb such as "Returns".
- Document class attributes and Pydantic fields with an attribute docstring on
  the line after the declaration. Pydantic models set
  `use_attribute_docstrings=True` so the text also reaches the JSON schema.
- Enforced by Ruff `D` (convention `google`) plus preview rules `D420`, `D421`,
  and `DOC*`, selected by exact code in `pyproject.toml`. Ruff's `D` rules
  check public names only, and `tests/` ignores `D` and `DOC`, so review
  every private name and test helper for its docstring.
- Docstrings are read in code and IDE hovers only; there is no generated
  documentation site.

## Structure

- `src/job_status_found/app/` holds only composition: the composition root
  `app.py` and `alembic_metadata.py`, which imports every feature's tables
  package so Alembic sees the whole schema. No feature imports anything from
  `app/`; `app/` imports features.
- `features/core/` holds code that several features or `app/` use, laid out
  like any feature. It owns:
  - the database shell in `infrastructure/db/db.py`: the declarative `Base`,
    the column types such as `SurrogateKey`, the engine lifespan
    `open_database`, and the request session `get_database_session`;
  - the `Clock` and `UnitOfWork` ports, their `SystemClock` and
    `SqlUnitOfWork` adapters, and the `get_clock` and `get_unit_of_work`
    providers in `core/di.py`. A feature's `di.py` injects them, so its
    repositories and its unit of work share one request session;
  - the RFC 9457 error shape (schemas, response helpers, the 422 handler, and
    `ProblemDetailsFastAPI`, which documents them);
  - clients for external systems that several features use, in
    `infrastructure/clients/`, one per system, such as
    `SmtpEmailSenderClient` with a general `send(recipient, subject, body)`
    that raises `EmailDeliveryFailure`. The client knows transport, never
    content: a feature's own adapter, such as auth's `SmtpAuthEmailSender`,
    writes its emails, sends them through the client from
    `get_smtp_email_sender_client`, and decides what a failure means;
  - `app_settings.py` with `AppSettings` (`JSF_*`) and the cached
    `get_settings()`: every application-wide value, such as the service
    name, CORS, the database (`JSF_DATABASE_*`), and the shared clients, such
    as the SMTP server (`JSF_SMTP_*`). A migration run loads it, so each of
    its values has a default or comes from `.env`;
  - `settings_config`, which every settings class uses.

  A port or adapter moves into core once a second feature needs it; one that
  holds a feature's own rule or key, such as
  `VerificationCodeHasher` with the auth HMAC key, stays in that feature. A feature
  maps each of its failures to a problem once, in a handler that `app.py`
  registers. Code outside core imports only its facade,
  `job_status_found.features.core`, and every name it publishes is in that
  `__init__.py`. Core imports no other feature and nothing from `app/`. Code
  that another feature needs but that depends on one feature, such as the
  auth guards, stays in that feature and goes out through its facade.
- A feature's root holds only `__init__.py`, `di.py`, and, when the feature
  has its own configuration, `<feature>_settings.py`; everything else sits in
  a layer. `<feature>_settings.py` defines a `<Feature>Settings` class with
  prefix `JSF_<FEATURE>_` and a cached `get_<feature>_settings()`, such as
  `features/auth/auth_settings.py` with `AuthSettings` and
  `get_auth_settings()`. It holds only values no other feature uses; an
  application-wide value goes into core's `AppSettings`, whose file is
  `app_settings.py` instead. Only `di.py` and infrastructure read it. `di.py`
  passes values to use cases and adapters, and gives a controller a value it
  needs through a provider, such as `get_sign_up_min_response_time`.
- A feature's use cases live in `application/use_cases/`, such as
  `check_health_use_case.py` with `CheckHealthUseCase`.
- A use case's constructor takes each collaborator (every port, such as a
  repository, hasher, clock, or sender) as its own keyword-only argument,
  such as `users: UserRepository`. Never bundle collaborators into a container
  object such as `SignUpPorts`: each dependency stays visible in the signature
  and in `di.py`. Configured values may share one frozen settings dataclass,
  such as `SignUpSettings`. Ruff's `PLR0913` is off for `application/use_cases/`
  for this reason.
- `features/<name>/di.py` provides each use case as
  `get_<verb>_<noun>_use_case`, injected with `Depends`, and passes every
  collaborator by keyword.
- HTTP adapters live in `presentation/http/`:
  - One controller module per endpoint, named for what it does:
    `<operation>_controller.py`, such as `sign_up_controller.py` or
    `health_controller.py`. It holds one `APIRouter` without a prefix or tag,
    one handler with its own path segment, such as `/sign-up`, and its
    OpenAPI metadata.
  - Every feature has `<feature>_router.py`, such as `auth_router.py` or
    `health_router.py`, even with one endpoint. It includes every
    controller's router under the feature's one tag and its prefix, if it has
    one, such as `/auth`. `app/app.py`
    includes that router, never a controller directly.
  - Request and response bodies live in `presentation/http/schemas/`, one
    Pydantic model per module: `<subject>_request.py` with `<Subject>Request`,
    such as `SignUpRequest`, and `<subject>_response.py` with
    `<Subject>Response`, such as `HealthStatusResponse`. Use cases never
    receive or return these models.
  - Failure-to-problem handlers live in `<feature>_exception_handlers.py`.
- SQLAlchemy mapped tables live in
  `features/<feature>/infrastructure/db/tables/`, one `<name>_table.py` per
  table, re-exported from that package. Declare each column by annotation
  alone, such as `email: Mapped[str]` or `id: Mapped[SurrogateKey]`, and keys,
  constraints, and indexes in `__table_args__`. Never assign `mapped_column()`:
  it returns `MappedColumn[Any]`, which ty's `unsound-assignment` rejects.
  Build a row as `UserTable()` and then assign each column as an attribute,
  which ty checks. Never pass columns as constructor keywords: SQLAlchemy types
  that constructor as `**kw: Any`, so ty cannot see a misspelled or mistyped
  column. Register each feature's tables package in `app/alembic_metadata.py`.
  Revisions live in `migrations/versions/`; read every operation of a
  generated revision before applying it.
- Tests live in `tests/{unit,integration}/` followed by the module's path
  under `src/job_status_found/`, as `test_<module>.py`, such as
  `tests/integration/features/health/presentation/http/test_health_controller.py`.
  A controller's test is named after its module, such as
  `test_sign_up_controller.py`, and a schema's test sits under `schemas/`.
- A unit test replaces a collaborator with a `unittest.mock` double, never a
  hand-written fake class: `create_autospec(<Port>, instance=True)`, so a call
  that does not match the port's signature fails.
- Mock-based tests live in a `Test<Subject>` class that sets its mocks up
  explicitly and tears them down:
  - `setup_method` creates fresh mocks as attributes, stubs what every test in
    the class shares, and builds the subject by passing each mock directly by
    keyword, such as `users=self.users`. Never bundle mocks into a holder
    object or hide the construction in a fixture.
  - `teardown_method` resets every mock with
    `reset_mock(return_value=True, side_effect=True)`, or stops a patch
    started in `setup_method`, such as `patch.object(aiosmtplib, "send",
    autospec=True)`.
  - Use `setup_class` and `teardown_class` only for an expensive resource the
    tests cannot change; mocks are always per test.
- A test stubs what decides its own case in the Given step with
  `return_value` or `side_effect`, and asserts the awaited calls that make up
  the effect, such as `assert_awaited_once_with` or `assert_not_awaited`.
  Record call order across mocks with `attach_mock` on one `Mock()`.
  A revision's test mirrors its path under `migrations/`.
- A revision's test runs it against a throwaway PostgreSQL database. It checks
  only what the database does: upgrade from empty, downgrade to base, no
  difference from the mapped tables, and the rules PostgreSQL itself enforces,
  such as `CHECK` constraints, foreign-key actions, and unique or partial
  indexes. Never write a test that restates the ERD or inspects SQLAlchemy
  metadata: `alembic check` in the checks below catches unregistered tables
  and drift between the tables and the revisions.

## Checks

The integration tests and `alembic check` need the Compose PostgreSQL, and the
auth integration tests need Mailpit; start both first. See the README when
port 5432, 1025, or 8025 is taken.

```shell
docker compose up --wait postgres mailpit
uv run alembic upgrade head
uv run alembic check
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov
```

