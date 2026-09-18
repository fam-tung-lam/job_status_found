# T-02: Sign-up emails a code or a notice and never reveals existing accounts

- Status: planned
- Spec trace: §6.1 (request part), §6.2 (hashing cost), §7 `POST /sign-up`,
  §9 (password policy length, enumeration, CORS, secrets, notices), §10
  (ports, settings, Compose), §11.2 (terms version)
- Blocked by: T-01
- Blocks: T-03

## Outcome

`POST /v1/auth/sign-up` answers 202 with the same body in every case. Mailpit
then receives either a 6-digit verification code or an "you already have an
account" notice.

## Context

- §6.1 defines three branches: a new email, the email of a verified user, and
  the email of an unverified user. The third branch overwrites the password
  hash and name, because nobody has proven that mailbox yet; whoever holds the
  mailbox decides by entering the code.
- The body and the timing must be the same in every branch, so the endpoint
  does not reveal which emails have accounts (§6.1, §9).
- A code is stored as HMAC-SHA-256 with a server key, because a 6-digit code
  has too little entropy for a bare hash (§9).
- Argon2id at 64 MiB must neither block the event loop nor exhaust the 512 MiB
  container (§6.2).
- The app sends no terms version. The backend stamps `terms_version` from its
  own setting (§11.2).
- This is the first auth endpoint, the first `POST` from a browser, and the
  first problem response. Later tickets reuse the error format, the hasher, the
  mail sender, and the challenge logic.

## In scope

- `SignUpWithPasswordUseCase` and `POST /v1/auth/sign-up` with first name,
  last name, email, and password.
- Email normalization: NFKC and lower case into `email_normalized`; `email`
  keeps the typed form (ERD).
- The length part of the password policy: 12 to 128 Unicode code points, else
  `password_too_weak` (§9). The breach check lands in T-15.
- `PasswordHasher` on `pwdlib[argon2]` 0.3.1 with
  `PasswordHash.recommended()`, run through `anyio.to_thread` behind a
  semaphore of 4 (§4, §6.2).
- The `verify_email` challenge: a 6-digit code, stored as an HMAC-SHA-256
  `secret_hash`, valid for 15 minutes. A new challenge replaces the open one
  (ERD).
- The 60-second interval between verification-code sends (§5, R-2).
- `AuthEmailSender` port with an `aiosmtplib` 5.1.3 SMTP adapter, the code
  email, and the existing-account notice (§4, §9). Mail goes out after the
  commit; a send failure is logged (§10).
- Mailpit in `docker-compose.override.yml` (§10).
- `terms_version` and `terms_accepted_at` stamped from settings.
- `Clock` and `SecretGenerator` ports, so expiry and codes are deterministic
  (§10).
- `pydantic[email]` for `EmailStr` (§4).
- RFC 9457 problem responses with the `code` member, the §7 status mapping,
  and exception handlers registered in `app/app.py` (§7).
- The CORS change in `app/app.py`: `allow_credentials=True`, the existing
  origin regex, methods `GET, POST, PUT, DELETE`, headers
  `Authorization, Content-Type` (§9).
- Settings under `JSF_AUTH_`: HMAC key as `SecretStr`, SMTP host, port,
  credentials, and sender, terms version, and the verification code's lifetime
  and send interval, with placeholders in `apps/backend/.env.example` (R-1).

## Out of scope

- Confirming or resending the code (T-03).
- The breach check (T-15) and the sign-up IP throttle (T-14).
- The app's sign-up page (T-08).

## Acceptance

- A new email creates an unverified user, an Argon2id password credential, and
  one open `verify_email` challenge, and Mailpit receives a 6-digit code
  (§6.1).
- The email of a verified user changes no row, and Mailpit receives the
  existing-account notice (§6.1, §9).
- The email of an unverified user replaces its password hash and name, and
  Mailpit receives a new code that replaces the open one (§6.1).
- Within 60 seconds of the previous code for the same user, no new code is
  sent and the open code stays valid (§5, R-2).
- All branches return 202 with an identical body, and response times do not
  reveal the branch (§6.1, §9).
- A password shorter than 12 or longer than 128 code points returns 400
  `password_too_weak` as `application/problem+json` (§7, §9).
- Invalid input returns 422 (§7).
- No stored value holds the code or the password in the clear. No log record
  or `auth_events` row holds a password, code, or raw email (§9).
- A browser on an allowed origin can send a credentialed `POST` (§9).
- The new user's `terms_version` equals the configured version (§11.2).

## Evidence required

- The three sign-up branches, each with its stored state and email (§14).
- An identical response body across branches, and timings that do not separate
  them.
- The policy boundaries at 11, 12, 128, and 129 code points, counted in code
  points rather than bytes.
- The problem response shape and status for `password_too_weak`.
- The 60-second send interval at its boundary.

## Implementation freedom

- How equal timing is achieved, for example hashing in every branch and
  sending mail after the response.
- Email wording and format, within §9's rules.
- Which `auth_events` types sign-up records. The spec names only
  `sign_in_failed` and `refresh_token_reused`.
- Backend limits on name length. The app enforces 1 to 100 characters (§11.2).
- Request field names, within `snake_case` (§7).
