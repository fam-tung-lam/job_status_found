# T-05: A verified person signs in with email and password through the API

- Status: implemented
- Spec trace: §5 (`remember_me`), §6.2 (sign-in), §7 `POST /sign-in`, §9
  (enumeration, logging), §10 (`PasswordSignInFailure`), §11.2 (no policy at
  sign-in)
- Blocked by: T-03
- Blocks: T-07

## Outcome

`POST /v1/auth/sign-in` returns a `TokenPairResponse` to a verified person with the
right password. Otherwise it fails with `invalid_credentials`,
`email_verification_required`, or `account_unavailable`.

## Context

- An unknown email and a wrong password must take the same time and fail with
  the same code. A dummy Argon2id verification runs for an unknown email or a
  social-only user (§6.2).
- A right password on an unverified user sends a fresh code and fails with
  `email_verification_required`, so the app can open the code page (§6.2).
- The account throttle in T-14 counts the `sign_in_failed` rows this ticket
  starts writing, so the audit trail and the throttle share one source of
  truth (ERD).
- The password policy is never applied at sign-in, because older passwords
  must keep working (§11.2).

## In scope

- `SignInWithPasswordUseCase` and `POST /v1/auth/sign-in`. The request carries
  email, password, `client_kind`, and `remember_me` (§5).
- `PasswordSignInFailure` with `PasswordSignInInvalidCredentialsFailure`,
  `PasswordSignInEmailNotVerifiedFailure`, and `PasswordSignInAccountUnavailableFailure`
  (§10). `PasswordSignInThrottledFailure` lands in T-14.
- The dummy verification for an unknown email or a social-only user (§6.2).
- An unverified user with the right password: a fresh `verify_email` code,
  subject to the 60-second interval, then 403 `email_verification_required`
  (§6.2, R-2).
- A suspended or pending-deletion user with the right password: 403
  `account_unavailable` (§7, R-9).
- `verify_and_update` rehashes a password stored with older parameters (§6.2).
- One `sign_in_failed` `auth_events` row per failed password check, with
  `identifier_hash` (HMAC-SHA-256 of the normalized email), IP address, and
  user agent (§9, ERD).
- Session issuance from T-03 with `sign_in_method` `password`.

## Out of scope

- The account and IP throttles (T-14).
- The app's sign-in page (T-07).

## Acceptance

- A verified, active user with the right password gets 200 `TokenPairResponse` and a
  new session, delivered per `client_kind` (§5, §7).
- An unknown email, a wrong password, and a social-only user all get 401
  `invalid_credentials` with `WWW-Authenticate: Bearer`, and their response
  times do not separate them (§6.2, §7).
- An unverified user with the right password gets 403
  `email_verification_required`, and Mailpit receives a fresh code unless one
  went out in the last 60 seconds (§6.2).
- A suspended or pending-deletion user with the right password gets 403
  `account_unavailable`; with a wrong password, `invalid_credentials` (§7,
  R-9).
- A hash stored with weaker parameters is replaced at the next successful
  sign-in (§6.2).
- Every failed password check writes one `sign_in_failed` row, also for an
  unknown email, and the same normalized email always yields the same
  `identifier_hash` (§9, ERD).
- No row or log record holds the raw email or the password (§9).
- A 12-character minimum is not enforced at sign-in (§11.2).

## Evidence required

- Each outcome above.
- Timing parity between an unknown email, a wrong password, and a social-only
  user.
- The rehash of older parameters.
- `sign_in_failed` rows for known and unknown identifiers.

## Evidence recorded

All paths are under `apps/backend/`. The completed backend check passed 159
tests at 96.20% coverage, together with Ruff, `ty`, and the migration checks.

| Evidence | Where |
|----------|-------|
| Unknown-email and social-only dummy verification, hashed audit event, successful rehash, and session commit | `tests/unit/features/auth/application/use_cases/test_sign_in_with_password_use_case.py` |
| Verified success, unverified resend, suspended-account disclosure only after a valid password, and the HTTP failure contract | `tests/integration/features/auth/presentation/http/v1/test_session_flow.py` |
| Controlled local timing parity | Fresh migrated disposable PostgreSQL, production Argon2, 2 warmups plus 15 interleaved requests per class: medians 26.99 ms social-only, 29.05 ms unknown, and 29.19 ms wrong password; maximum median spread 2.20 ms (8.15%); means 27.99/28.93/28.94 ms; p90 30.00/30.30/30.50 ms |

The timing result is controlled local evidence, not a production network
measurement. It is sufficient to show that the three branches perform the
same dominant Argon2 work without a material local separation.

## Implementation notes

- Unknown, wrong-password, and social-only branches share
  `invalid_credentials`; each failed password check records one
  `sign_in_failed` event with a keyed identifier hash.
- Account state is disclosed only after the submitted password verifies.
  Passwords stored with old parameters are rehashed before the successful
  session transaction commits.

## Implementation freedom

- The contents of `auth_events.details`, within §9.
- How the dummy verification obtains its hash.
