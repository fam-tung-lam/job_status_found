# T-01: An operator migrates a fresh database to the auth schema

- Status: planned
- Spec trace: §10 (shell files, first revision), §14 (metadata contract), ERD
  (all eight tables, keys, constraints, indexes)
- Blocked by: None
- Blocks: T-02, T-16

## Outcome

Running the Alembic upgrade against the Compose PostgreSQL 18 database creates
the eight auth tables with their keys, constraints, and indexes. Running the
downgrade removes them.

## Context

- The backend has no persistence code yet.
  `apps/backend/src/job_status_found/app/` holds only `app.py` and
  `app_settings.py`, and `pyproject.toml` has no
  SQLAlchemy, driver, or Alembic dependency.
- `app_settings.py` already reads the `JSF_DATABASE_*` values, and
  `apps/backend/docker-compose.yml` already runs PostgreSQL 18.
- The ERD owns every table, column, key, constraint, and index. The spec never
  repeats them, and this ticket must not either: build from the ERD.
- §10 fixes that the first revision creates all eight tables. Later tickets add
  no tables.
- The persistence convention in the backend code-style skill asks for a
  metadata contract test whose expectations come from the agreed schema, not
  from the models.

## In scope

- Runtime dependencies `sqlalchemy[asyncio]` 2.0.54, `psycopg[binary]` 3.3.6,
  and `alembic` 1.20.0 (§4).
- `app/db.py`: declarative `Base`, async engine, session factory, and the
  request session dependency (§10). The application lifespan owns the engine.
- `app/alembic_metadata.py`, `alembic.ini`, and `migrations/` (§10).
- One `<name>_table.py` per ERD table in
  `features/auth/infrastructure/persistence/models/`.
- The first revision, with every ERD convention:
  - `uuid` surrogate keys with `DEFAULT uuidv7()`;
  - `timestamptz` for every instant, nullable where the ERD says so;
  - `text` plus a `CHECK` constraint for each closed vocabulary, never a
    PostgreSQL `ENUM`;
  - `ON DELETE CASCADE` on every foreign key to `users`, except
    `auth_events.user_id`, which is `ON DELETE SET NULL`;
  - the unique constraints on `users.email_normalized`,
    `external_identities (provider, provider_subject)` and
    `(user_id, provider)`, `refresh_tokens.token_hash`,
    `oauth_authorization_attempts.state_hash`, and
    `oauth_authorization_attempts.exchange_code_hash`;
  - the `CHECK` that keeps `sessions.revocation_reason` null exactly when
    `revoked_at` is null;
  - the indexes `sessions (user_id) WHERE revoked_at IS NULL`, the partial
    unique index `email_challenges (user_id, purpose) WHERE consumed_at IS NULL`,
    `email_challenges (secret_hash)`, and the three `auth_events` indexes.
- A documented way to run the migration against the Compose database.

## Out of scope

- Every endpoint, use case, and repository adapter (T-02 onward).
- Retention deletes (T-16).

## Acceptance

- On an empty PostgreSQL 18 database, the upgrade creates exactly the eight
  ERD tables, and the downgrade removes them (§10).
- Each table's columns, types, nullability, defaults, keys, `CHECK`
  constraints, and indexes match the ERD.
- Deleting a `users` row removes its rows in every other table and sets
  `auth_events.user_id` to null (ERD).
- A `sessions` row with `revoked_at` set and `revocation_reason` null, or the
  reverse, is rejected by the database (ERD).
- A value outside a closed vocabulary, such as a `sessions.client_kind` of
  `desktop`, is rejected by the database (ERD).
- The metadata that Alembic loads lists the eight tables (§14).
- The existing health endpoint and backend checks still pass.

## Evidence required

- The metadata contract of §14: the metadata Alembic loads exposes the eight
  agreed tables, with expectations written from the ERD.
- An upgrade and a downgrade against a real PostgreSQL 18.
- The cascade, set-null, revocation-reason, and vocabulary rules enforced by
  the database itself.

## Implementation freedom

- How migrations run in Compose: a one-off command, an entrypoint step, or a
  separate service.
- Revision naming and layout inside `migrations/`.
- Engine and pool options.
- The delete rules on `refresh_tokens.session_id` and
  `refresh_tokens.parent_token_id`, which the ERD leaves open. They must let
  T-16 delete a session and an expired parent token without a foreign-key
  error.
