# T-01: An operator migrates a fresh database to the auth schema

- Status: implemented
- Spec trace: §10 (shell files, first revision), §14 (migration checks), ERD
  (all eight tables, keys, constraints, indexes)
- Blocked by: None
- Blocks: T-02, T-16

## Outcome

Running the Alembic upgrade against the Compose PostgreSQL 18 database creates
the eight auth tables with their keys, constraints, and indexes. Running the
downgrade removes them.

## Context

- Before this ticket, the backend had no persistence code.
  `apps/backend/src/job_status_found/app/` held only `app.py` and
  `app_settings.py`, and `pyproject.toml` had no SQLAlchemy, driver, or
  Alembic dependency.
- `app_settings.py` already reads the `JSF_DATABASE_*` values, and
  `apps/backend/docker-compose.yml` already runs PostgreSQL 18.
- The ERD owns every table, column, key, constraint, and index. The spec never
  repeats them, and this ticket must not either: build from the ERD.
- §10 fixes that the first revision creates all eight tables. Later tickets add
  no tables.

## In scope

- Runtime dependencies `sqlalchemy[asyncio]` 2.0.54, `psycopg[binary]` 3.3.6,
  and `alembic` 1.20.0 (§4).
- `db/db.py`: declarative `Base`, async engine, session factory, and the
  request session dependency (§10). The application lifespan owns the engine.
- `db/alembic_metadata.py`, `alembic.ini`, and `migrations/` (§10).
- One `<name>_table.py` per ERD table in
  `features/auth/infrastructure/db/tables/`.
- The first revision, with every ERD convention:
  - `uuid` surrogate keys with `DEFAULT uuidv7()`;
  - `timestamptz` for every instant, nullable where the ERD says so;
  - `text` plus a `CHECK` constraint for each closed vocabulary, never a
    PostgreSQL `ENUM`;
  - `ON DELETE CASCADE` on every foreign key to `users`, except
    `auth_events.user_id`, which is `ON DELETE SET NULL`;
  - `ON DELETE CASCADE` on `refresh_tokens.session_id` and
    `ON DELETE SET NULL` on `refresh_tokens.parent_token_id`;
  - the unique constraints on `users.email_normalized`,
    `external_identities (provider, provider_subject)` and
    `(user_id, provider)`, `refresh_tokens.token_hash`,
    `oauth_authorization_attempts.state_hash`, and
    `oauth_authorization_attempts.exchange_code_hash`;
  - the `CHECK` that keeps `sessions.revocation_reason` null exactly when
    `revoked_at` is null;
  - the indexes `sessions (user_id)`, `refresh_tokens (session_id)`,
    `refresh_tokens (parent_token_id)`, the partial unique index
    `email_challenges (user_id, purpose) WHERE consumed_at IS NULL`,
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
- Deleting a session removes its refresh tokens, and deleting a parent refresh
  token keeps its child with a null `parent_token_id` (ERD).
- A `sessions` row with `revoked_at` set and `revocation_reason` null, or the
  reverse, is rejected by the database (ERD).
- A value outside a closed vocabulary, such as a `sessions.client_kind` of
  `desktop`, is rejected by the database (ERD).
- `alembic check` against a database at head reports no difference from the
  mapped tables (§14).
- The existing health endpoint and backend checks still pass.

## Evidence required

- An upgrade and a downgrade against a real PostgreSQL 18, with no difference
  between the upgraded schema and the mapped tables (§14).
- The cascade, set-null, revocation-reason, vocabulary, and open-challenge
  rules enforced by the database itself.

## Implementation freedom

- How migrations run in Compose: a one-off command, an entrypoint step, or a
  separate service.
- Revision naming and layout inside `migrations/`.
- Engine and pool options.
