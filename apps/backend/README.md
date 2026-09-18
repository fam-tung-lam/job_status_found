# job-status-found backend

FastAPI service managed with uv (Python 3.14).

```shell
# install runtime and dev tools
uv sync
uv run uvicorn job_status_found.main:app --reload
```

## Docker

The stack is the backend plus PostgreSQL 18. Copy `.env.example` to `.env` and
set `JSF_DATABASE_PASSWORD` first; Compose refuses to start without
`JSF_DATABASE_NAME`, `JSF_DATABASE_USER`, and `JSF_DATABASE_PASSWORD`.

```shell
# development: editable install, auto-reload, source synced on change
docker compose up --build --watch

# PostgreSQL only, for a backend started on the host with `uv run`
docker compose up --wait postgres

# production-like: hardened runtime image, no development overrides
docker compose -f docker-compose.yml up --build --wait

# production image alone
docker build -t job-status-found-backend .
```

- `Dockerfile` has a `dev` target and a `runtime` target, which is the default.
  The runtime image holds only the virtual environment, `alembic.ini`, and
  `migrations/`, and runs as UID 10001. Development builds are tagged
  `job-status-found-backend:dev`, so they never replace the runtime image.
- `docker-compose.yml` is the production-like stack.
  `docker-compose.override.yml` adds the development setup and loads
  automatically.
- Both services publish on `127.0.0.1` only: the backend on `BACKEND_PORT`
  (default 8000) and, in development, PostgreSQL on `JSF_DATABASE_PORT`
  (default 5432).
- `.env` holds one set of `JSF_DATABASE_*` values. Compose creates the
  PostgreSQL role and database from them and passes them to the backend
  container with `JSF_DATABASE_HOST=postgres`; a backend started on the host
  reads the same file and connects to `localhost`. The backend container
  starts after PostgreSQL accepts TCP connections.
- PostgreSQL applies the name, user, and password only when it first
  initialises the data volume, so changing the password later also needs
  `ALTER ROLE ... PASSWORD`.
- Both services have memory, CPU, and process limits, and rotate their logs at
  3 x 10 MB.
- The dev container runs the `uv run` checks below, such as
  `docker compose exec backend uv run pytest --cov`.
- Behind a reverse proxy, set `FORWARDED_ALLOW_IPS` on the backend to the
  proxy's address so uvicorn trusts its `X-Forwarded-*` headers.
- Data lives in the `postgres-data` volume. `docker compose down --volumes`
  deletes it.
- Base images are pinned by tag and digest in `Dockerfile` and
  `docker-compose.yml`; Dependabot raises them. Keep the uv image inside the
  `uv_build` range in `pyproject.toml`.

## Migrations

Alembic owns the schema. `migrations/env.py` reads the database location from
the same `JSF_DATABASE_*` settings as the app, so `alembic.ini` holds no URL.

```shell
# host, against the Compose PostgreSQL (`JSF_DATABASE_PORT` picks its port)
uv run alembic upgrade head

# development container
docker compose exec backend alembic upgrade head

# production-like stack: rebuild first, because the runtime image ships the revisions
docker compose -f docker-compose.yml run --build --rm backend alembic upgrade head

# new revision: generate, then read every operation before applying it
uv run alembic revision --autogenerate -m "describe the change"
```

- The app starts without the schema; a request that needs a table fails until
  the upgrade has run.
- Mapped tables live in `features/<feature>/infrastructure/db/tables/`. A
  feature's tables reach Alembic only after its tables package is imported in
  `src/job_status_found/db/alembic_metadata.py`.
- `uv run alembic check` compares the mapped tables with a database at head
  without writing a revision. It fails on a table whose package was never
  registered and on differing columns, types, nullability, server defaults,
  foreign keys, unique constraints, indexes, and added or removed `CHECK`
  constraints. It does not compare a `CHECK` constraint's text, primary keys,
  or partial-index conditions, so read those in every revision.

## Checks

```shell
docker compose up --wait postgres
uv run alembic upgrade head
uv run alembic check
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov
```

`alembic check` and the integration tests need the Compose PostgreSQL. The
migration tests create throwaway databases on that server and drop them
afterwards, so the development data stays untouched. When another service
already holds port 5432, set another port in `.env`, such as
`JSF_DATABASE_PORT=55432`. Compose publishes PostgreSQL on it, and every host
command above connects to it, while the backend container keeps using 5432.

Docstring rules live in [AGENTS.md](AGENTS.md).

Settings are read from `JSF_`-prefixed environment variables or `.env`
(see `src/job_status_found/app/app_settings.py`).

Browsers may call the API only from origins matching
`JSF_CORS_ALLOW_ORIGIN_REGEX`. The default allows any `localhost` or
`127.0.0.1` port, which covers `flutter run -d chrome`.
