# T-14: Repeated attempts are throttled per account and per IP

- Status: planned
- Spec trace: §4 (`limits`), §7 (429 `too_many_attempts`, `Retry-After`), §9
  (account throttle, IP throttle), §10 (`RequestThrottle`,
  `PasswordSignInThrottled`), ERD (`auth_events` indexes)
- Blocked by: T-09
- Blocks: T-17

## Outcome

After 5 failed sign-ins for one email in 15 minutes, or when an IP exceeds a
route group's limit, the API answers 429 `too_many_attempts` with a
`Retry-After` header.

## Context

- The account throttle counts recent `sign_in_failed` rows, which T-05 writes.
  The audit trail and the throttle share one source of truth (ERD).
- `identifier_hash` lets the throttle group attempts against an email that has
  no account (ERD).
- The account throttle is a block, not a permanent lock, so it cannot lock a
  victim out for good (§9).
- `limits` 5.8.0 with async in-memory storage is correct for one worker (§4).
- The route groups that exist now are sign-in, sign-up, code confirm, and reset
  request. The exchange group lands with its endpoint in T-17.
- The app already shows the `too_many_attempts` message from T-07.

## In scope

- The account throttle in `SignInWithPasswordUseCase`: 5 `sign_in_failed`
  events per `identifier_hash` in 15 minutes block further password checks for
  that identifier for 15 minutes, raising `PasswordSignInThrottled` (§9, §10).
- `RequestThrottle` port with a `limits` moving-window adapter per route group:
  sign-in 10/min, sign-up 5/min, code confirm 10/15 min, reset request 3/5 min
  (§9).
- The client IP comes from `X-Forwarded-For` only when Uvicorn's
  `--forwarded-allow-ips` names the proxy (§9).
- 429 problem responses with `too_many_attempts` and `Retry-After` (§7).

## Out of scope

- The exchange group, 20/min (T-17).
- Redis storage for `limits` (README, deferred until a second worker).

## Acceptance

- The sixth password check for one identifier within 15 minutes returns 429
  `too_many_attempts` without verifying the password, and `Retry-After` states
  when the block ends (§7, §9).
- After the block, sign-in with the right password works again (§9).
- The account block also applies to an email that has no account (ERD).
- Each route group returns 429 with `Retry-After` once one IP exceeds its limit
  in the moving window (§9).
- A forged `X-Forwarded-For` from a client that is not a named proxy does not
  change the throttled IP (§9).
- The app shows "Too many attempts. Try again in N minutes." from a real 429
  (§11.2).

## Evidence required

- The account throttle at its boundaries: the fifth and sixth failures, the
  window edge, and the end of the block.
- Each route group's limit.
- Trust of the forwarded header.

## Implementation freedom

- Whether the throttle numbers are settings.
- How `Retry-After` is computed for the account block.
