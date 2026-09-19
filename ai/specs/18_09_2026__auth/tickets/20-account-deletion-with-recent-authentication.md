# T-20: A signed-in person deletes their account after a fresh password proof

- Status: planned
- Spec trace: §5 (recent authentication), §6.6 (step 1), §7
  `POST /reauthentication`, `DELETE /me`, §8 rule 5, §10
  (auth guards)
- Blocked by: T-06
- Blocks: T-21, T-22, T-23, T-24, T-26

## Outcome

A person whose last credential proof is at most 10 minutes old deletes their
account with `DELETE /v1/auth/me`. A person with an older proof first
re-authenticates with `POST /v1/auth/reauthentication`.

## Context

- Setting a first password, changing the email, linking or unlinking a
  provider, and deleting the account require `sessions.authenticated_at` to be
  at most 10 minutes old. Otherwise the endpoint fails with
  `recent_authentication_required`, and the app asks for the password (§5).
- `require_recent_authentication` loads the session row, so it reacts
  immediately, unlike the 15-minute access token (§5, §8 rule 5).
- This ticket introduces the guard with its first consumer (R-6). T-21, T-22,
  T-23, and T-26 reuse it.
- App Store guideline 5.1.1(v) requires in-app deletion, but §11 specifies no
  deletion page (README).

## In scope

- `require_recent_authentication` in
  `features/auth/presentation/http/v1/guards/authentication_guards.py`, published
  through the auth facade, with the
  10-minute window as a setting (§5, §8 rule 5, §10).
- `ReauthenticateWithPasswordUseCase` and `POST /v1/auth/reauthentication`
  (Bearer): the right password sets the session's `authenticated_at` to now
  and answers 204; a wrong one fails with 401 `invalid_credentials` (§7).
- `RequestAccountDeletionUseCase` and `DELETE /v1/auth/me` (Recent): set
  `deletion_requested_at`, revoke every session with `account_deleted`, and
  answer 202 (§6.6).

## Out of scope

- Deleting the `users` row (T-16).
- Re-authentication with Google (T-24).
- A deletion page (README).

## Acceptance

- With `authenticated_at` at most 10 minutes old, `DELETE /me` returns 202,
  sets `deletion_requested_at`, and revokes every session with
  `account_deleted` (§6.6).
- With an older `authenticated_at`, `DELETE /me` returns 403
  `recent_authentication_required` and changes nothing (§5, §7).
- `POST /reauthentication` with the right password returns 204, and the next
  `DELETE /me` succeeds. A wrong password returns 401 `invalid_credentials`
  (§7).
- After deletion, password sign-in with the right password returns
  `account_unavailable`, every refresh fails with `session_ended`, and a reset
  request sends nothing (§5, §6.2, §6.6).
- The guard decides from the session row, so a still-valid access token
  cannot bypass a closed window (§5).

## Evidence required

- The 10-minute window at its boundary (§14).
- Sign-in, refresh, and reset request after deletion.

## Implementation freedom

- How the guard exposes the session row to the handler.
