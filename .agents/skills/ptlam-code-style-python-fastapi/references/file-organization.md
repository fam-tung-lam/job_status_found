# FastAPI Project Structure

A feature-first, four-layer default for a FastAPI service that has no stronger
layout. Preserve a coherent existing structure and reorganize only files owned
by the requested change. Reorganization is not a deliverable.

## Grow into this structure

Keep a small application flat until a second business capability makes feature
packages useful. Once a capability owns a feature package, put its code under
`application/`, `domain/`, `infrastructure/`, or `presentation/`. Create a
package when its first owned file appears.

Keep the feature's `dtos/` folder under `application/`, never under
`infrastructure/`.

## The project tree

```text
project/
├── pyproject.toml
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
├── src/
│   └── myapp/                             # one importable package named for the service
│       ├── __init__.py
│       ├── main.py                        # ASGI entrypoint: app = create_app()
│       ├── app/                           # application shell
│       │   ├── __init__.py
│       │   ├── app.py                     # create_app(): the composition root
│       │   ├── settings.py                # Settings plus one cached accessor
│       │   ├── db.py                      # Base, engine, session factory, dependency
│       │   └── alembic_metadata.py        # imports every feature's persistence models
│       ├── integrations/
│       │   ├── redis.py
│       │   ├── celery_app.py
│       │   └── s3.py
│       ├── shared/                        # framework-neutral, proven cross-feature reuse
│       │   ├── errors.py
│       │   ├── logging_config.py
│       │   ├── pagination.py
│       │   └── clock.py
│       └── features/
│           ├── __init__.py
│           ├── health/                    # liveness; a normal feature
│           │   ├── __init__.py
│           │   ├── di.py
│           │   ├── application/
│           │   │   ├── __init__.py
│           │   │   ├── dtos/
│           │   │   │   ├── __init__.py
│           │   │   │   └── health_status.py
│           │   │   └── use_cases/
│           │   │       ├── __init__.py
│           │   │       └── check_health.py
│           │   └── presentation/
│           │       ├── __init__.py
│           │       └── http/
│           │           ├── __init__.py
│           │           └── health_controller.py
│           └── users/                     # one business capability
│               ├── __init__.py            # facade; the only cross-feature import path
│               ├── di.py                  # FastAPI feature composition and providers
│               ├── application/
│               │   ├── __init__.py
│               │   ├── dtos/              # validated application input and output
│               │   │   ├── __init__.py
│               │   │   ├── create_user.py
│               │   │   └── user.py
│               │   ├── ports/             # repository and outbound contracts
│               │   │   ├── __init__.py
│               │   │   └── user_repository.py
│               │   └── use_cases/         # one application operation per file
│               │       ├── __init__.py
│               │       ├── create_user.py
│               │       └── get_user.py
│               ├── domain/
│               │   ├── __init__.py
│               │   ├── entities/
│               │   │   ├── __init__.py
│               │   │   └── user.py
│               │   ├── failures/
│               │   │   ├── __init__.py
│               │   │   └── user_not_found.py
│               │   └── value_objects/
│               │       ├── __init__.py
│               │       └── email.py
│               ├── infrastructure/
│               │   ├── __init__.py
│               │   ├── adapters/          # application-port implementations
│               │   │   ├── __init__.py
│               │   │   └── sql_user_repository.py
│               │   └── persistence/
│               │       ├── __init__.py
│               │       └── models/        # SQLAlchemy mapped tables
│               │           ├── __init__.py
│               │           ├── user_table.py
│               │           └── profile_table.py
│               └── presentation/          # inbound FastAPI and worker adapters
│                   ├── __init__.py
│                   ├── http/
│                   │   ├── __init__.py
│                   │   └── users_controller.py
│                   └── tasks/
│                       ├── __init__.py
│                       └── send_welcome_email.py
└── tests/
    ├── conftest.py
    ├── app/                               # the assembled app
    │   └── integration/
    │       └── test_app.py
    └── features/                          # mirrors src/myapp/features/
        ├── health/
        │   ├── unit/
        │   │   └── application/
        │   │       └── use_cases/
        │   │           └── test_check_health.py
        │   └── integration/
        │       └── presentation/
        │           └── test_health_controller.py
        └── users/
            ├── conftest.py
            ├── test_doubles/
            │   └── fake_user_repository.py
            ├── unit/
            │   ├── application/
            │   │   └── use_cases/
            │   │       ├── test_create_user.py
            │   │       └── test_get_user.py
            │   └── domain/
            └── integration/
                ├── infrastructure/
                │   └── test_sql_user_repository.py
                └── presentation/
                    └── test_users_controller.py
```

Keep this tree as plain text so it renders in every editor, terminal, diff, and
code review without a renderer-version requirement. Python package names stay
lowercase with underscores, so the folder is `use_cases/`, not `use-cases/`.

## Give each service location one role

| Path                      | Owns                                                                                         |
| ------------------------- | -------------------------------------------------------------------------------------------- |
| `main.py`                 | Nothing except `app = create_app()`                                                          |
| `app/app.py`              | `FastAPI`, lifespan, middleware, feature routers, and exception handlers; no business policy |
| `app/settings.py`         | One-time configuration: the Settings model and its cached accessor                           |
| `app/db.py`               | One-time engine and session setup                                                            |
| `app/alembic_metadata.py` | Imports every feature's persistence models and exposes complete metadata to Alembic          |
| `integrations/`           | One client or pool facade per external system; not the feature behavior that consumes it     |
| `shared/`                 | Framework-neutral code with at least two proven feature consumers                            |
| `features/<feature>/`     | One business capability, its facade, composition file, and four layers                       |

The `app/` package is the application shell. Add `app/db.py` and
`app/alembic_metadata.py` with the first database. Health is an ordinary feature
under `features/health/`; add readiness or build information as a feature only
when a consumer needs it. Every package's `__init__.py`, including
`app/__init__.py` and `features/__init__.py`, carries the docstring that
[documentation.md](documentation.md) requires.

## Give each feature layer one role

| Path                                 | Owns                                                                              |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| `__init__.py`                        | Public facade: selected application and domain types with real external consumers |
| `di.py`                              | `Depends` providers that connect presentation, use cases, ports, and adapters     |
| `application/dtos/`                  | Pydantic application input and output contracts; no FastAPI transport context     |
| `application/ports/`                 | Repository and outbound protocols consumed by use cases                           |
| `application/use_cases/`             | One transport-neutral application operation per verb-first file                   |
| `domain/entities/`                   | Persistence-independent business entities with identity                           |
| `domain/failures/`                   | Stable failures callers may handle                                                |
| `domain/value_objects/`              | Immutable domain values identified by their contents                              |
| `infrastructure/adapters/`           | SQL, storage, and vendor implementations of application ports                     |
| `infrastructure/persistence/models/` | SQLAlchemy mapped tables and persistence-owned enums                              |
| `presentation/http/`                 | `<resource>_controller.py` modules: `APIRouter`, handlers, auth, and HTTP mapping |
| `presentation/tasks/`                | Thin durable-job, schedule, listener, and command entry points                    |

Use `__init__.py` as the facade instead of a stuttering `<feature>_module.py`.
Export no presentation or infrastructure internals. `di.py` is the feature
composition seam, like a Nest feature module; it may know both framework
dependencies and concrete adapters, but it owns no policy.

Keep SQLAlchemy models distinct from domain entities. Infrastructure adapters
map persistence rows and vendor responses to domain types before returning
through an application port.

## Keep optional folders narrow

Keep a helper or constant in its only consumer's file. When another file in the
same layer needs it, give it a narrowly named module there; add a package only
for a real grouping. Never add feature-root `utils/`, `helpers/`, `models/`, or
`constants/` buckets that hide layer ownership.

Name every HTTP router module `<resource>_controller.py`, such as
`health_controller.py`, and its test `test_<resource>_controller.py`. Never use
a bare `controller.py`: the name is ambiguous in imports, editor tabs, stack
traces, and search. One router module may own related handlers on one
`APIRouter`; [routes.md](routes.md) owns splitting independent HTTP resources.
Keep `di.py` as provider composition, with use-case and adapter implementations
in their layer files.

Do not add `helpers.py`, `misc.py`, `common.py`, or `general.py`, and do not
shadow standard-library modules such as `types.py`, `logging.py`, `email.py`,
`secrets.py`, `queue.py`, `json.py`, or `datetime.py`.

Finish when the service has one importable package, `main.py` only builds the
app from `app/`, every feature sits under `features/` and publishes one facade,
every router module has a resource name, every feature implementation file apart
from `__init__.py` and `di.py` sits in one explicit layer, shared code has
proven consumers, SQLAlchemy models stay in infrastructure, and source and test
trees expose the same capability and layer ownership.
