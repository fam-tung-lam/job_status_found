# FastAPI Application Composition

How the application owns its lifetime, settings, router assembly, middleware,
framework-wide handlers, and observability.

Keep one composition root. In the default layout, `create_app()` in `app/app.py`
creates `FastAPI`, installs middleware and exception handlers, and includes
every feature router from `features/<feature>/presentation/http/` once. That
import is composition, not a cross-feature dependency. `main.py` stays at the
package root and holds only the ASGI entry point:

```python
from myapp.app.app import create_app

app = create_app()
```

Keep a coherent existing factory location. Feature packages never change the app
while being imported.

## Own the process lifetime

Use `FastAPI(lifespan=...)` with an async context manager for application-wide
resources. Acquire before `yield` and close after it. Do not mix lifespan with
the deprecated startup and shutdown event handlers; FastAPI runs one model or
the other.

Acquire only application-wide, concurrency-safe clients and pools in lifespan,
never at module import. Acquire request-specific sessions and connections in
dependencies. Expose a started resource through a typed dependency rather than a
mutable global that tests must patch before importing the app.

The [FastAPI lifespan guide](https://fastapi.tiangolo.com/advanced/events/)
identifies the feature; it is not required reading. When the installed FastAPI
or Starlette behaves differently, read the locked packages and prove the startup
and shutdown contract with a focused local test.

Importing a module for a unit test must not open a connection, dispatch a job,
or register anything remotely.

## Compose once

- Read settings through the project's settings owner. Do not scatter direct
  environment reads across handlers and use cases. In a new service, define one
  Pydantic Settings model and one cached accessor in `app/settings.py`.
- Include the health feature's router without an API version prefix. Add
  readiness or build information as a feature only when a consumer needs it.
- Give each shared path prefix, version prefix, tag, and dependency one
  inclusion site.
- Order middleware on purpose. Middleware that records a response must see the
  exception and response transformations it is meant to observe.
- Configure access logging, error capture, and correlation once. Record the
  method, canonical path, status, duration, and correlation identifier that
  operators need.
- Make query, header, request-body, and error-body capture opt-in, bounded, and
  redacted. Let one outer boundary capture an unexpected error after middleware
  records and re-raises it.
- Mount static files and optional subsystems only when their files exist; make a
  missing required file fail startup clearly.

## Share infrastructure, not feature behavior

Build one client or pool per external system under `integrations/` and expose it
through a typed facade. Features receive that facade through dependencies; they
never build a second Redis, S3, mail, payment, or queue client.

Configure the timeout, the connection limit, and any retry policy on that
facade, once. A client built without an explicit timeout inherits an unbounded
one and holds a worker until the far side answers.

Keep the Celery app in `integrations/celery_app.py`. Keep each task under
`features/<feature>/presentation/tasks/` and register it on that app. A task
assembles and calls the same use case as the HTTP route; business policy lives
in neither the facade nor the task shell.

Finish when app construction is repeatable in tests, startup and shutdown own
the same resources, and each router, handler, and middleware is installed once.
