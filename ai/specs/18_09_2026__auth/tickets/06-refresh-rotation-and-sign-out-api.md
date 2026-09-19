# T-06: Sessions refresh by rotation, detect reuse, and end on sign-out

- Status: implemented
- Spec trace: D-2, §5 (refresh token steps 1 to 5, delivery by client kind,
  cookie endpoints, lifetimes, refresh reuse grace), §7 `POST /token/refresh`,
  `POST /sign-out`, §10 (`SessionRefreshFailure`)
- Blocked by: T-04
- Blocks: T-07, T-12, T-13, T-20

## Outcome

`POST /v1/auth/token/refresh` rotates the refresh token and returns a new
`TokenPairResponse`. Replaying a spent token ends the session. `POST /v1/auth/sign-out`
ends it on request.

## Context

- RFC 9700 requires rotation or sender-constraining for public clients; a
  session row makes revocation real (D-2).
- Refresh tokens of one session form a family. Presenting a used or revoked
  token revokes the whole session, so both the thief and the owner must sign
  in again (§5, ERD).
- The web app restores its session after a reload by calling refresh; the
  browser attaches the cookie (§5).
- The cookie endpoints also require an `Origin` header that matches the CORS
  allow-list. With `SameSite=Strict`, that closes CSRF (§5).
- This ticket introduces session revocation with a reason. T-10, T-12, T-13,
  and T-20 reuse it.

## In scope

- `RefreshSessionUseCase` in one transaction with the session row locked,
  following §5:
  1. No row for the token's hash: fail with `refresh_token_invalid`.
  2. Session revoked or past either expiry, or user suspended or pending
     deletion: fail with `session_ended`.
  3. Token unused and not revoked: set `used_at`, insert a child token, move
     `idle_expires_at` to `min(now + idle lifetime, absolute_expires_at)`, and
     return a new access token and the child.
  4. Token used less than 10 seconds ago with a child that is still unused:
     revoke that child, insert a new one, and return it.
  5. Any other used or revoked token: revoke the session with
     `refresh_token_reused`, record an `auth_events` row, and fail with
     `session_ended`.
- The session's stored `client_kind` decides the channel: the cookie for `web`,
  the body for `ios` and `android` (§5).
- The `Origin` check on the cookie endpoints (§5).
- `SignOutUseCase` and `POST /v1/auth/sign-out`, accepting the refresh token
  (cookie or body) or the bearer token. It revokes the session with
  `signed_out`, revokes its refresh tokens, clears the cookie, and returns 204
  (§7, ERD).
- `SessionRefreshFailure` with `SessionRefreshTokenInvalidFailure` and
  `SessionRefreshSessionEndedFailure` (§10).
- Session revocation that sets `revoked_at` and `revocation_reason` together
  and revokes the session's refresh tokens (ERD).

## Out of scope

- Revoking sessions after a password reset or change (T-10, T-12), by the user
  (T-13), or on account deletion (T-20).
- The app's use of refresh (T-07) and its sign-out control (T-11).

## Acceptance

- Each of the five §5 outcomes produces its stated result. Failures are 401
  `refresh_token_invalid` or 401 `session_ended` (§5, §7).
- After step 3, the old token is used, the child works, and `idle_expires_at`
  never passes `absolute_expires_at` (§5).
- A retry within the 10-second grace gets a fresh child and the session stays
  open. The same retry after the grace revokes the session with
  `refresh_token_reused` and writes an `auth_events` row (§5).
- A web session rotates its cookie and never returns `refresh_token` in the
  body, whatever the request asks for (§5).
- A cookie request without a matching `Origin` is rejected (§5).
- Sign-out through the cookie, a body refresh token, or a bearer token returns
  204, revokes the session with `signed_out`, and clears the web cookie. The
  session's refresh token then fails with `session_ended` (§7).
- Sign-out promises no failure code (§7).
- Two concurrent refreshes of the same token cannot both pass step 3 (§5).

## Evidence required

- The five refresh outcomes (§14).
- The 10-second grace boundary and the clamp of the idle expiry to the
  absolute expiry (§14).
- `session_ended` for a revoked, idle-expired, absolute-expired, suspended,
  and pending-deletion session.
- The cookie flow with and without a matching `Origin`.
- Sign-out through each of its three credentials.

## Evidence recorded

All paths are under `apps/backend/`. The completed backend check passed 159
tests at 96.20% coverage, together with Ruff, `ty`, and the migration checks.

| Evidence | Where |
|----------|-------|
| Rotation, idle-expiry clamp, grace retry, exact grace boundary, origin rejection, and every ended-session state | `tests/unit/features/auth/application/use_cases/test_refresh_session_use_case.py` |
| Unknown and exact-expiry refresh tokens, web cookie rotation, and concurrent PostgreSQL refresh locking | `tests/integration/features/auth/presentation/http/v1/test_session_flow.py` |
| Refresh-token precedence, bearer fallback only for an unknown refresh token, and recognized spent-token sign-out | `tests/unit/features/auth/application/use_cases/test_sign_out_use_case.py` |
| Cookie, body, and bearer sign-out in the HTTP contract | `tests/integration/features/auth/presentation/http/v1/test_session_flow.py` |

## Implementation notes

- Refresh locks both the session and matching refresh-token rows. The real
  PostgreSQL concurrency check proves two simultaneous rotations cannot both
  create a normal active child.
- Normal rotation marks the parent `used_at`; it does not revoke it. A lost
  response retried inside the grace window revokes the unused child before
  issuing its replacement. Ending a session revokes the whole token family.
- Sign-out uses any recognized refresh-token hash, including a spent or
  revoked token, to identify and revoke that token's session. It falls back to
  the bearer principal only when no refresh-token row exists.

## Implementation freedom

- The status and code of a failed `Origin` check; §7 promises none.
- How the row lock is taken.
