---
name: ptlam-code-style-python-fastapi
description:
  Write, review, and fix Python and FastAPI code against conventions for the
  toolchain, modules and imports, typing, async work, Pydantic, docstrings,
  logging, pytest, service and four-layer feature-package structure, application
  lifespan, routes, request and response contracts, dependency injection, use
  cases, feature boundaries, model registration, concurrency, errors,
  observability, and API tests. Use when starting or standardizing a Python
  FastAPI service, adding or changing endpoints, use cases, dependencies,
  exception handlers, middleware, schemas, SQLAlchemy registration, background
  handoffs, or tests, or fixing type, lint, test, OpenAPI, and runtime failures.
  Do not use for Python code that does not run in a FastAPI service.
---

# PTLam Python FastAPI Code Style

Rules for Python and FastAPI code: the development toolchain, package
boundaries, imports, typing, async work, Pydantic models, docstrings, logging,
and pytest, then four-layer feature packages, application composition and
lifespan, HTTP contracts, dependencies, use cases, persistence registration,
concurrency, errors, observability, and API tests. This skill owns Python and
FastAPI mechanics; the foundation owns everything else.

## Required skills

### `ptlam-code-style`

**Reason:** Provides the language-neutral conventions and testing doctrine the Python and FastAPI mechanics satisfy. This skill does not repeat them.

**Instructions:** Loading the foundation is required, not optional background.

1. Read `skills/ptlam-code-style/SKILL.md` in full before any review
   or change.
2. Before each task, read every foundation reference the table below
   names for it. Paths are relative to this skill.
3. Record each foundation reference you read for the Finish list.

| Task                                                         | Read first under `skills/ptlam-code-style/references/`                         |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| Any review or change                                         | `complexity.md`                                                                |
| Adding or moving a file, module, package, or feature         | `structure.md`, `boundaries.md`, `naming.md`                                   |
| Writing or changing a function body                          | `readability.md`, `naming.md`                                                  |
| Adding or changing a public name, docstring, or comment      | `documentation.md`, `naming.md`                                                |
| Designing a DTO, entity, value object, table, or state set   | `data-modeling.md`                                                             |
| Changing a route, schema, event, or other published contract | `contracts.md`, `evolution.md`                                                 |
| Raising, translating, retrying, or mapping a failure         | `errors.md`                                                                    |
| Starting async work, a background handoff, or lifespan       | `async-lifecycle.md`                                                           |
| Emitting or configuring logs                                 | `logging.md`                                                                   |
| Adding a dependency, abstraction, or shared helper           | `complexity.md`, `evolution.md`                                                |
| Writing or changing a test                                   | `behavior-contract.md`, `test-levels/`, `test-placement.md`, `test-doubles.md` |

Rules agents most often miss:

- Every test uses Given-When-Then; in pytest, write explicit
  `# Given:`, `# When:`, and `# Then:` comments.
- A test checks behavior through a public interface, never private
  methods or internal call counts.
- Expected values come from a specification, worked example, or
  literal, never from the production algorithm.
- A test name states what the caller observes, not the mechanism.
- A higher test level covers only a risk the lower one cannot, and no
  assertion repeats across levels.
- Red-Green-Refactor applies only when the user asks for test-first
  work by name.
- Stubbing stays in the Given phase, with fresh doubles per test.
- Comments explain why, and a deliberate deviation carries its reason
  where it lives.
- A failure is never swallowed, and every retry is bounded.
- A log record is written once per event and never holds a secret or
  personal data.
- An unresolved conflict is reported, never settled quietly.

This skill may be stricter than the foundation, never less strict.
The foundation's "Who decides" table resolves any conflict.

Read [ptlam-code-style](skills/ptlam-code-style/SKILL.md).

## Before review or change

Choose review or change using the foundation's mode policy. In review, use
installed tools without dependency sync, package builds, or installation;
[dev-toolchain.md](references/dev-toolchain.md) gives the check-mode commands.
Inspect migration setup and use the persistence reference's schema comparison;
never generate or apply a revision to satisfy a review check.

1. Resolve the service root and read every applicable `AGENTS.md` from the
   repository root down to the files in scope.
2. Read `pyproject.toml`, the lock or constraints files, CI, the application
   entry point, and the nearest source and tests. Note the minimum Python
   version, package and build layout, formatter, linter, type checker, test
   runner, and their real commands; the installed FastAPI, Starlette, and
   Pydantic versions; and whether each database, HTTP, storage, and queue client
   is sync or async.
3. Treat executable configuration, CI, and verified code as the truth. An
   installed dependency does not prove the project runs it, and a stray legacy
   pattern does not become a rule or weaken these rules to match it.
4. Map the source and test tree. Trace one request through router inclusion,
   dependency injection, the handler, the application DTO, the use case, the
   port, the infrastructure adapter, the session or client, exception handlers,
   middleware, and tests. Give every prefix, resource, transaction, and error
   translation one owner.
5. Apply the stricter rules to code you add or substantially change. Leave
   unrelated legacy inconsistencies alone.

For a new project, use uv for environments and the lock, Ruff for formatting and
linting, ty for type checking, and pytest with pytest-mock, pytest-cov, and
pytest-asyncio. In an existing project, keep its working toolchain until
replacing it is part of the task.

## Pick a reference

| Concern                                                                             | Reference                                                   |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Creating or standardizing the environment, checks, or CI                            | [dev-toolchain.md](references/dev-toolchain.md)             |
| Adding a module, publishing a name, or fixing an import cycle                       | [modules-and-imports.md](references/modules-and-imports.md) |
| Writing or changing annotations, value types, or runtime checks                     | [typing.md](references/typing.md)                           |
| Defining or serializing a Pydantic model (Pydantic v2 installed)                    | [pydantic.md](references/pydantic.md)                       |
| Writing a docstring or generating API docs                                          | [documentation.md](references/documentation.md)             |
| Emitting or configuring logs                                                        | [logging.md](references/logging.md)                         |
| Starting or reorganizing the service package, feature layers, shared code, or tests | [file-organization.md](references/file-organization.md)     |
| Building the app, startup and shutdown, settings, routers, middleware, or logging   | [application.md](references/application.md)                 |
| Declaring a path, request input, response output, paging, status, or OpenAPI        | [routes.md](references/routes.md)                           |
| Injecting authentication, a session, request context, or another capability         | [dependencies.md](references/dependencies.md)               |
| Doing I/O, choosing `def` or `async def`, streaming, or a background handoff        | [concurrency.md](references/concurrency.md)                 |
| Tracing or enforcing the route-to-use-case-to-repository pipeline                   | [architecture.md](references/architecture.md)               |
| Designing a use case or its transaction boundary                                    | [use-cases.md](references/use-cases.md)                     |
| Publishing a feature facade, enforcing imports, or breaking a feature cycle         | [feature-boundaries.md](references/feature-boundaries.md)   |
| Registering SQLAlchemy models or wiring Alembic metadata                            | [persistence.md](references/persistence.md)                 |
| Raising, translating, or mapping a failure to an HTTP response                      | [errors.md](references/errors.md)                           |
| Writing, placing, or reshaping a pytest test, or testing an endpoint or lifespan    | [testing.md](references/testing.md)                         |

SQLAlchemy queries and mappings, Alembic revisions, Celery execution, Sentry
capture, and other integrations keep their own repository mechanics. This skill
owns feature placement, model registration, FastAPI lifetime, transport, and
handoff seams.

## Do the work

1. State the observable contract: method, canonical path, authentication,
   inputs, success status and body, and each promised error. Keep every changed
   public surface intentional and compatible with the supported Python versions.
2. Trace one path from a presentation adapter through one application DTO, use
   case, port, and infrastructure adapter to the session or client. Remove any
   second read or write lane in changed code.
3. Give changed production callables precise parameter and return types. Keep
   runtime validation separate from static typing.
4. Choose sync or async execution from the whole call path. Keep blocking work
   out of async paths, and close every resource on success, failure, and
   cancellation.
5. Assemble the use case in a typed dependency. Keep the handler at the HTTP
   boundary, give the use case the transaction decision, and return a declared
   response shape.
6. Map failures once. When the API allows deferred work, return an accepted
   response only after a durable handoff succeeds.
7. Add or update behavior tests in the existing test home. Cover the normal,
   boundary, and failure cases the change touches; for an endpoint, test
   success, invalid input, authentication and authorization, domain failure, and
   the stored or queued effect through the ASGI app.
8. Run checks narrow to broad: focused tests, configured checks on changed
   files, then project-wide gates. Inspect OpenAPI for a public contract change,
   and run `alembic check` and the import-boundary checks when affected.
9. In change mode, run the package build and supported version matrix when
   distribution or compatibility is affected. Install a changed distributed
   package's built artifact in a throwaway environment and smoke-test its
   changed public imports.

Inspect the diff after any write-mode formatter or hook. Report the exact
commands, their results, configured exclusions that affect confidence, every
unrun service, and every check you did not run.

## Finish

1. List every foundation reference you read in the handoff.
2. Confirm the change meets the criteria below.

Finish when every feature file sits under `application/`, `domain/`,
`infrastructure/`, or `presentation/` with only `__init__.py` and `di.py` at the
feature root; the changed code keeps its package and serialization contracts and
adds no new type or lint failure; no event loop is blocked and no resource
leaks; dispatch and dependency scopes match the resource APIs; every changed
route uses the one request pipeline; feature imports enter facades; registered
metadata holds every mapped table; OpenAPI matches the intended contract; and
the affected behavior tests, including isolated ASGI tests, pass under the
project's real toolchain.
