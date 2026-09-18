# Backend agent notes

## Docstrings

- Style: Google (`Args:`, `Returns:`, `Yields:`, `Raises:`, `Attributes:`,
  `Example:`). Do not mix NumPy or Sphinx field styles.
- Every public module, package, class, function, method, and property has a
  docstring. `_private` names and `tests/` are exempt.
- Do not repeat types; annotations carry them.
- Property docstrings describe the value ("Whether...", "The..."), never start
  with a verb such as "Returns".
- Document class attributes and Pydantic fields with an attribute docstring on
  the line after the declaration. Pydantic models set
  `use_attribute_docstrings=True` so the text also reaches the JSON schema.
- Enforced by Ruff `D` (convention `google`) plus preview rules `D420`, `D421`,
  and `DOC*`, selected by exact code in `pyproject.toml`.
- Docstrings are read in code and IDE hovers only; there is no generated
  documentation site.

## Structure

- `src/job_status_found/app/` holds the composition root `app.py` and
  `app_settings.py`.
- `src/job_status_found/db/` holds the database shell: `db.py` with the
  declarative `Base`, the engine lifespan, and the request session, and
  `alembic_metadata.py` with the schema Alembic migrates.
- A feature's use cases live in `application/use_cases/`, such as
  `check_health_use_case.py` with `CheckHealthUseCase`.
- `features/<name>/di.py` provides each use case as
  `get_<verb>_<noun>_use_case`, injected with `Depends`.
- HTTP adapters live in `presentation/http/`: `<name>_controller.py` and a
  Pydantic `<Subject>Response` model per response body, such as
  `HealthStatusResponse`. Use cases never return these models.
- SQLAlchemy mapped tables live in
  `features/<feature>/infrastructure/db/tables/`, one `<name>_table.py` per
  table, re-exported from that package. Declare each column by annotation
  alone, such as `email: Mapped[str]` or `id: Mapped[SurrogateKey]`, and keys,
  constraints, and indexes in `__table_args__`. Never assign `mapped_column()`:
  it returns `MappedColumn[Any]`, which ty's `unsound-assignment` rejects.
  Build a row as `UserTable()` and then assign each column as an attribute,
  which ty checks. Never pass columns as constructor keywords: SQLAlchemy types
  that constructor as `**kw: Any`, so ty cannot see a misspelled or mistyped
  column. Register each feature's tables package in `db/alembic_metadata.py`.
  Revisions live in `migrations/versions/`; read every operation of a
  generated revision before applying it.
- Tests live in `tests/{unit,integration}/` followed by the module's path
  under `src/job_status_found/`, as `test_<module>.py`, such as
  `tests/integration/features/health/presentation/http/test_health_controller.py`.
  A revision's test mirrors its path under `migrations/`.
- A revision's test runs it against a throwaway PostgreSQL database. It checks
  only what the database does: upgrade from empty, downgrade to base, no
  difference from the mapped tables, and the rules PostgreSQL itself enforces,
  such as `CHECK` constraints, foreign-key actions, and unique or partial
  indexes. Never write a test that restates the ERD or inspects SQLAlchemy
  metadata: `alembic check` in the checks below catches unregistered tables
  and drift between the tables and the revisions.

## Checks

The integration tests and `alembic check` need the Compose PostgreSQL; start
it first. See the README when port 5432 is taken.

```shell
docker compose up --wait postgres
uv run alembic upgrade head
uv run alembic check
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov
```

