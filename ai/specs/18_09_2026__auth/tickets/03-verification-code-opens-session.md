# T-03: The emailed code verifies the email and opens a session

- Status: implemented
- Spec trace: §5 (access token issuance, refresh token, delivery by client
  kind, lifetimes, `remember_me`), §6.1 (confirm part), §7
  `POST /email-verification/confirm`, `POST /email-verification/resend`, §9
  (enumeration)
- Blocked by: T-02
- Blocks: T-04, T-05

## Outcome

Submitting the right code and matching password to
`POST /v1/auth/email-verification/confirm` marks the email verified and
returns a `TokenPair`. A `web` client receives its refresh token only as an
`HttpOnly` cookie.

## Context

- A session is one sign-in on one device, bound to a `sessions` row. Its
  refresh tokens form one family (ERD).
- `client_kind` (`web`, `ios`, `android`) is sent at sign-in and fixes the
  refresh-token channel for the session's whole life (§5).
- Every request that creates a session carries `remember_me`, stored as
  `sessions.is_persistent`; it picks the lifetimes (§5).
- A script on the web page must never read a long-lived credential (D-3).
- This ticket introduces session issuance. T-05, T-17, and T-25 reuse it.
- T-02 left these for this ticket to reuse: the problem helpers in the
  `features.core` facade and the exception handlers registered in
  `app/app.py`, `AuthSettings`, the `EmailChallengeRepository` and
  `AuthEmailSender` ports with their adapters, the
  `generate_verification_code`, `hash_verification_code`, and `utc_now`
  helpers, the deferred mail after the response, and the sign-up's
  minimum response time, which resend needs for the same enumeration reason.
- Confirmation binds the code to the password the person intends to verify.
  The request carries both values, and the backend accepts neither in
  isolation.
- Failed code-password pairs are capped per user across replacement
  challenges. The cap is five failures in the rolling configured verification
  lifetime, 15 minutes by default.

## In scope

- `ConfirmEmailVerificationUseCase` and its endpoint. The request carries the
  email, code, password, `client_kind`, and `remember_me`.
  - The open `verify_email` challenge is found by `(user_id, purpose)` and
    checked for HMAC, expiry, and attempt count (ERD).
  - A wrong code or password writes one `email_verification_failed` event.
    The fifth failed pair within the rolling verification lifetime consumes
    the current challenge (§6.1).
  - Success consumes the challenge, sets `email_verified_at`, and creates the
    session.
- `ResendEmailVerificationUseCase` and its endpoint: always 202. Only an
  unverified user gets a new code, which replaces the open one, at most once
  per 60 seconds (§5, §9).
- Session issuance:
  - a `sessions` row with `sign_in_method` `password`, `client_kind`,
    `is_persistent`, `ip_address`, `user_agent` truncated to 512 characters,
    `authenticated_at`, `last_refreshed_at`, `idle_expires_at`, and
    `absolute_expires_at` (ERD);
  - a refresh token from `secrets.token_urlsafe(32)`, stored only as SHA-256,
    with `expires_at` copied from the session's idle expiry (§5, ERD);
  - `AccessTokenCodec` on `pyjwt[crypto]` 2.14.0: HS256, header
    `typ=at+jwt` and `kid`, claims `iss`, `aud` (`job-status-found-api`),
    `sub`, `sid`, `role`, `iat`, `exp`, `jti`, lifetime 15 minutes (§5);
  - `TokenPair` with `access_token`, `expires_in`, `token_type`, and
    `refresh_token`, which is absent for `web` (§7);
  - for `web`, `Set-Cookie: __Secure-jsf_refresh=...; HttpOnly; Secure;
    SameSite=Strict; Path=/v1/auth`, with `Max-Age` only for a persistent
    session (§5).
- Lifetimes: persistent sessions 30 days idle and 180 days absolute;
  non-persistent sessions 24 hours idle and 7 days absolute (§5).
- Settings: issuer, audience, the JWT key ring (`kid` to secret, one signing
  key, any number of verify-only keys), lifetimes, cookie name, and the cookie
  `secure` flag. `JSF_AUTH_COOKIE_SECURE=false` and a cookie name without the
  `__Secure-` prefix are for local `http://localhost` only (§5, §10).

## Out of scope

- Verifying access tokens and `GET /me` (T-04).
- Refresh and sign-out (T-06).
- The code-confirm IP throttle (T-14).
- The app's verification page (T-08).

## Acceptance

- The right code and matching password within 15 minutes set
  `email_verified_at`, consume the challenge, create one session and one
  refresh token, and return 200 `TokenPair` (§6.1, §7).
- For `ios` and `android`, the body carries `refresh_token` (§5).
- For `web`, the body has no `refresh_token`, and the response sets the cookie
  with `HttpOnly; Secure; SameSite=Strict; Path=/v1/auth` (§5).
- A non-persistent web session's cookie has no `Max-Age` (§5).
- The session's idle and absolute expiries match the `remember_me` choice
  (§5).
- The access token's header and claims match §5, and it expires 15 minutes
  after issue.
- A wrong code or password returns 400 `verification_code_invalid`, writes an
  `email_verification_failed` event, and commits it before raising. After the
  fifth failed pair in the rolling verification lifetime, the current
  challenge is consumed and the right pair also fails (§6.1, §7, §9).
- An expired code, a consumed code, and an email with no open challenge return
  the same `verification_code_invalid`; the unknown-email branch still pays
  for a dummy password verification (§7, §9).
- Resend returns 202 with an identical body for unknown, verified, and
  unverified emails. Only an unverified user receives a new code, at most once
  per 60 seconds (§5, §9).
- Only the refresh token's SHA-256 is stored; the access token is not stored
  (§5, §9).

## Evidence required

- Code attempt exhaustion (§14).
- Lifetime boundaries: code expiry at 15 minutes and both session lifetimes
  (§14).
- The token pair per client kind, including every cookie attribute.
- The access token's header and claims, signed with the configured key.
- Identical resend bodies for all branches.

## Evidence recorded

All paths are under `apps/backend/`. The completed backend check passed 159
tests at 96.20% coverage, together with Ruff, `ty`, and the migration checks.

| Evidence | Where |
|----------|-------|
| Password-bound success, committed atomically with verification and session issuance | `tests/unit/features/auth/application/use_cases/test_confirm_email_verification_use_case.py` |
| Rolling fifth-failure cap across a replacement challenge, event write, and exact expiry boundary | `tests/unit/features/auth/application/use_cases/test_confirm_email_verification_use_case.py` |
| Unknown-email dummy password work | `tests/unit/features/auth/application/use_cases/test_confirm_email_verification_use_case.py` |
| Resend enumeration and the 60-second branch | `tests/unit/features/auth/application/use_cases/test_resend_email_verification_use_case.py` |
| Mobile body delivery, web cookie delivery, session lifetimes, and the complete HTTP flow | `tests/integration/features/auth/presentation/http/test_session_flow.py` and `tests/unit/features/auth/presentation/http/test_token_pair_delivery.py` |
| JWT headers, claims, accepted key rotation, and rejection cases | `tests/unit/features/auth/infrastructure/adapters/test_jwt_access_token_codec.py` |

## Implementation notes

- All accepted-shape confirmation failures collapse to
  `verification_code_invalid`. Neither the code nor password mismatch is
  disclosed.
- The failure cap counts `email_verification_failed` events for the user since
  `now - verification_code_lifetime`, so replacing a challenge does not reset
  the attacker's allowance. The `(user_id, created_at)` index supports this
  query without a schema change.
- A web token pair omits the refresh token and uses the configured strict
  `HttpOnly` cookie. Mobile token pairs return the refresh token in the body.

## Implementation freedom

- `jti` format and `kid` naming.
- Where cookie handling lives in the presentation layer.
