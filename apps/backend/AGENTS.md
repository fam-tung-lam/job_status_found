# Backend agent notes

## Docstrings

- Style: Google (`Args:`, `Returns:`, `Yields:`, `Raises:`, `Attributes:`,
  `Example:`). Do not mix NumPy or Sphinx field styles.
- Every module, package, class, function, method, and property has a
  docstring, public or private (`_name`), in `src/` and `migrations/`. So does
  every module constant and class attribute: an attribute
  docstring on the line after it, such as `_SMTP_TIMEOUT_SECONDS`. A private
  docstring is concise: one sentence on what it does or holds, then the
  reason when the code does not show it.
- Instance attributes that `__init__` sets from its arguments are covered by
  its `Args:` section.
- Do not repeat types; annotations carry them.
- Property docstrings describe the value ("Whether...", "The..."), never start
  with a verb such as "Returns".
- Document class attributes and Pydantic fields with an attribute docstring on
  the line after the declaration. Pydantic models set
  `use_attribute_docstrings=True` so the text also reaches the JSON schema.
- Enforced by Ruff `D` (convention `google`) plus preview rules `D420`, `D421`,
  and `DOC*`, selected by exact code in `pyproject.toml`. Ruff's `D` rules
  check public names only, so review every private name for its docstring.
- Docstrings are read in code and IDE hovers only; there is no generated
  documentation site.

## Naming

- Names follow the root naming rules. A repository port method names its
  entity and effect, such as `set_password_hash` or
  `replace_open_email_challenge`, never a bare `save` or `record`. A method
  that returns `None` when no row matches starts with `find_`, or with
  `lock_` when it also locks the row.
- An exception message built before the `raise` goes in a variable named
  `error_message`, not `msg`.
- A repository method that reads or writes user data takes `owner_id`, per
  §8 rule 3 of the auth specification. Keep that name even where `user_id`
  reads more naturally.
- Keep the names a library requires or its documentation uses throughout,
  such as FastAPI's `lifespan`, SQLAlchemy's `Base`, Alembic's
  `run_migrations_online`, and Pydantic's `model_config`. Keep the wire
  fields of `InvalidInputErrorResponse` too: `loc`, `msg`, and `type`.
- Every class in `application/dtos/` ends in `DTO`, and its module ends in
  `_dto.py`, such as `TokenPairDTO` in `token_pair_dto.py`.
- Every request and response model ends in `Request` or `Response`, and its
  module ends in `_request.py` or `_response.py`.
- Every typed failure and each of its variants ends in `Failure`. Its module
  ends in `_failure.py`; variants of one operation may share the base
  failure's module.

## Code layout

- Code layout follows the root "Code layout and comments" rules, with `#`
  phase comments; `SignUpWithPasswordUseCase.invoke` shows the layout.
- `ruff format` keeps one blank line inside a function body and removes
  more, so one blank line is the phase separator.

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
  - the `UnitOfWork` port, its `SqlUnitOfWork` adapter, and the
    `get_unit_of_work` provider in `core/di.py`. A feature's `di.py` injects
    it, so its repositories and its unit of work share one request session;
  - the `utc_now` helper and its `get_utc_now` provider, which a feature's
    `di.py` injects, so callers can supply the clock;
  - the RFC 9457 error shape (schemas, response helpers, the 422 handler, and
    `ProblemDetailsFastAPI`, which documents them);
  - clients for external systems that several features use, in
    `infrastructure/clients/`, one per system, such as
    `SmtpEmailSenderClient` with a general
    `send_plain_text_email(recipient, subject, body)` that raises
    `EmailDeliveryFailure`. The client knows transport, never content: a
    feature's own adapter, such as auth's `SmtpAuthEmailSender`, writes its
    emails, sends them through the client from
    `get_smtp_email_sender_client`, and decides what a failure means;
  - `app_settings.py` with `AppSettings` (`JSF_*`) and the cached
    `get_app_settings()`: every application-wide value, such as the service
    name, CORS, the database (`JSF_DATABASE_*`), and the shared clients, such
    as the SMTP server (`JSF_SMTP_*`). A migration run loads it, so each of
    its values has a default or comes from `.env`;
  - `settings_config`, which every settings class uses.

  A port, adapter, or helper moves into core once a second feature needs it;
  one that holds a feature's own rule or key, such as
  `hash_verification_code` with the auth HMAC key, stays in that feature. A feature
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
- The application layer has no service classes or `services/` folder. Split
  every independently invokable business operation into its own use case,
  including an operation shared by other use cases. A use case reads or writes
  state only through repository ports. When one use case injects another to
  compose a larger transaction, the outer use case owns the unit-of-work
  commit.
- A collaborator with state or several operations, such as a repository, the
  unit of work, or an email sender, is a port: a `Protocol` in
  `application/ports/`, implemented by a class in `infrastructure/adapters/`.
- A single operation with no state of its own, such as hashing a password,
  generating or hashing a verification code, or reading the time, is a helper
  function instead, never a `Protocol` with an adapter class:
  - One function per file in `infrastructure/helpers/`, named verb first after
    what it does to which value, such as `hash_password.py` with
    `hash_password`. It sits in infrastructure because it wraps a library, the
    operating system, or a secret. A pure rule without any of those belongs in
    `domain/`, and a use case calls it directly.
  - The input comes first; configuration and shared resources follow as
    keyword-only arguments, such as `hmac_key` or `limiter`. `di.py` binds them
    with `functools.partial`, so the use case sees only the input.
  - A use case never imports a helper. It takes it as a keyword-only
    `Callable` argument named after it, such as
    `hash_password: Callable[[str], Awaitable[str]]`, and calls
    `self._hash_password(password)`.
  - `di.py` passes a helper directly, such as
    `generate_verification_code=generate_verification_code`. A helper that
    needs the request or request-scoped replacement gets a provider named
    `get_<helper>` instead, such as `get_hash_password`, which binds the
    lifespan's limiter, or `get_utc_now`.
  - A helper that gains state or a second operation becomes a port.
- A use case's constructor takes each collaborator (every port, such as a
  repository or sender, and every helper) as its own keyword-only argument,
  such as `users: UserRepository`. Never bundle collaborators into a container
  object such as `SignUpPorts`: each dependency stays visible in the signature
  and in `di.py`. Configured values may share one frozen settings dataclass,
  such as `SignUpSettings`. Ruff's `PLR0913` is off for `application/use_cases/`
  for this reason.
- `features/<name>/di.py` provides each use case as
  `get_<verb>_<noun>_use_case`, injected with `Depends`, and passes every
  collaborator by keyword.
- HTTP adapters live in `presentation/http/`. A versioned HTTP contract keeps
  its complete adapter subtree in `presentation/http/v<major>/`, such as
  `presentation/http/v1/`. This includes its controllers, feature router,
  schemas, helpers, exception handlers, guards, and version-specific settings.
  `app/app.py` mounts the router under the matching URL prefix. An endpoint
  intentionally shared across API versions, such as the health probe, stays
  directly in `presentation/http/`:
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
  - Request and response bodies live in the HTTP version's `schemas/`, one
    Pydantic model per module: `<subject>_request.py` with `<Subject>Request`,
    such as `SignUpRequest`, and `<subject>_response.py` with
    `<Subject>Response`, such as `HealthStatusResponse`. Use cases never
    receive or return these models.
  - A stateless operation that maps HTTP-specific values lives as one function
    per file in the HTTP version's `helpers/`, named after that function, such
    as `build_session_input_from_request.py`.
  - Failure-to-problem handlers live in
    `<version>/exception_handlers/<feature>_exception_handlers.py`.
  - Authentication and authorization dependencies live in
    the HTTP version's `guards/`, grouped by the concern they guard, such as
    `authentication_guards.py`.
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

## Testing

[`../../docs/testing_conventions_backend.md`](../../docs/testing_conventions_backend.md)
is authoritative for backend test structure, doubles, fixtures, isolation,
coverage, and checks. If it conflicts with this file, follow the testing
conventions.

- Test every controller as a local integration through the app's HTTP test
  client. Run the real downstream application components and replace only the
  lowest unavailable API outside our control.
