# T-16: Expired auth records and deleted accounts are purged on schedule

- Status: planned
- Spec trace: §6.6 (step 2), §10 (purge task), ERD (retention table, delete
  rules)
- Blocked by: T-01
- Blocks: None

## Outcome

An hourly run of
`python -m job_status_found.features.auth.presentation.tasks.purge_auth_records`
deletes every row past its retention and every user whose deletion was
requested.

## Context

- The ERD owns the retention schedule; §10 owns the task's shape.
- Every foreign key to `users` cascades, except `auth_events.user_id`, which
  becomes null, so the audit trail outlives the account without naming it
  (ERD).
- The task is idempotent, so overlapping runs are harmless (§10).
- The rows it deletes come from later tickets, but the task needs only the
  schema; seeded rows make it observable now.

## In scope

- `PurgeAuthRecordsUseCase` with the ERD schedule:
  - `email_challenges`, `oauth_authorization_attempts`, and `refresh_tokens`:
    1 day after `expires_at`;
  - `sessions`: 30 days after `revoked_at` or `absolute_expires_at`;
  - `auth_events`: 90 days after `created_at`;
  - `users`: once `deletion_requested_at` is set (§6.6 step 2).
- `presentation/tasks/purge_auth_records.py`, runnable with `python -m` (§10).
- An hourly schedule from the host's scheduler or a small Compose service
  (§10).

## Out of scope

- Setting `deletion_requested_at` (T-20).

## Acceptance

- Rows just inside each retention boundary stay, and rows just past it are
  deleted (ERD).
- A user with `deletion_requested_at` set is deleted with every dependent row,
  and their `auth_events` rows remain with `user_id` null (§6.6, ERD).
- Two runs in a row, or two overlapping runs, end in the same state without an
  error (§10).
- An hourly run is configured (§10).

## Evidence required

- Each retention boundary (§14).
- Idempotence under repeated and overlapping runs.
- The user purge cascade and the audit set-null.

## Implementation freedom

- Host scheduler or Compose service.
- Batch sizes and the task's log output.
