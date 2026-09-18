# T-12: A signed-in person changes an existing password

- Status: planned
- Spec trace: §5 (no recent-authentication window for a change), §6.2
  (change), §7 `PUT /password`, §9 (password policy, notices)
- Blocked by: T-06
- Blocks: T-15, T-22

## Outcome

`PUT /v1/auth/password` with the right current password stores the new
password, ends every other session of the account, and emails the "password
changed" notice.

## Context

- Changing an existing password needs no recent-authentication window, because
  the current password is part of the request (§5).
- Setting a first password for a social-only user is the other use of this
  endpoint. It waits on DEC-4 in T-22.
- No app page is specified for this; the result is visible through the API
  (README, deferred concerns).

## In scope

- `ChangePasswordUseCase` and `PUT /v1/auth/password` (Bearer) with the current
  and the new password, answering 204.
- A wrong current password: 401 `invalid_credentials` (§7).
- The new password checked against the §9 policy: 400 `password_too_weak`
  (R-8).
- Revocation of every other session of the user with `password_changed`; the
  requesting session stays (§6.2).
- The "password changed" notice (§9, R-3).

## Out of scope

- The first-password path (T-22).
- The breach check (T-15).

## Acceptance

- The right current password and a compliant new password return 204, and the
  next sign-in needs the new password (§6.2).
- Every other session of the user is revoked with `password_changed`, and its
  refresh token fails with `session_ended`. The requesting session keeps
  working (§6.2).
- The user receives the "password changed" notice (§9).
- A wrong current password returns 401 `invalid_credentials` and changes
  nothing (§7).
- A new password outside 12 to 128 code points returns 400
  `password_too_weak` and changes nothing (§9, R-8).

## Evidence required

- Each outcome above.
- The revocation scope: other sessions revoked, the requesting session kept.

## Implementation freedom

- Request field names, within `snake_case`.
- Which `auth_events` types a change records.
