# T-02: Sign-up emails a code or a notice and never reveals existing accounts

- Status: implemented
- Spec trace: §6.1 (request part), §6.2 (hashing cost), §7 `POST /sign-up`,
  §9 (password policy length, enumeration, CORS, secrets, notices), §10
  (ports, settings, Compose)
- Blocked by: T-01
- Blocks: T-03

## Outcome

`POST /v1/auth/sign-up` answers 202 with the same empty body in every case.
Mailpit then receives either a 6-digit verification code or an "you already
have an account" notice.

## Context

- §6.1 defines three branches: a new email, the email of a verified user, and
  the email of an unverified user. The third branch overwrites the password
  hash and name, because nobody has proven that mailbox yet, unless a code went
  out in the last 60 seconds. DEC-7 tracks why the code alone cannot tell the
  mailbox owner which password it confirms.
- The body and the timing must be the same in every branch, so the endpoint
  does not reveal which emails have accounts (§6.1, §9).
- A code is stored as HMAC-SHA-256 with a server key, because a 6-digit code
  has too little entropy for a bare hash (§9).
- Argon2id at 64 MiB must neither block the event loop nor exhaust the 512 MiB
  container (§6.2).
- This is the first auth endpoint, the first `POST` from a browser, and the
  first problem response. Later tickets reuse the error format, the hasher, the
  mail sender, and the challenge logic.

## In scope

- `SignUpWithPasswordUseCase` and `POST /v1/auth/sign-up` with first name,
  last name, email, and password.
- Email normalization: NFKC and lower case into `email_normalized`; `email`
  keeps the typed form as `email-validator` normalizes it (ERD).
- The length part of the password policy: 12 to 128 Unicode code points, else
  `password_too_weak` (§9). The breach check lands in T-15.
- `hash_password` on `pwdlib[argon2]` 0.3.1 with
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
- `Clock` and `SecretGenerator` ports, so expiry and codes are deterministic
  (§10). Built as `Clock` (now in core), `VerificationCodeGenerator`, and
  `VerificationCodeHasher`, since replaced by the injected helpers `utc_now`
  (core), `generate_verification_code`, and `hash_verification_code`.
- `pydantic[email]` for `EmailStr` (§4).
- RFC 9457 problem responses with the `code` member, the §7 status mapping,
  and exception handlers registered in `app/app.py` (§7).
- The CORS change in `app/app.py`: `allow_credentials=True`, the existing
  origin regex, methods `GET, POST, PUT, DELETE`, headers
  `Authorization, Content-Type` (§9).
- Settings under `JSF_AUTH_`: HMAC key as `SecretStr`, SMTP host, port,
  security, credentials, and sender, the password minimum, the verification
  code's lifetime and send interval, and the sign-up minimum response time,
  with placeholders in `apps/backend/.env.example` (R-1).

## Out of scope

- Confirming or resending the code (T-03).
- The breach check (T-15) and the sign-up IP throttle (T-14).
- The app's sign-up page (T-08).

## Acceptance

- A new email creates an unverified user, an Argon2id password credential, and
  one open `verify_email` challenge, and Mailpit receives a 6-digit code
  (§6.1).
- The email of a verified user changes no account data, and Mailpit receives
  the existing-account notice, at most once per 60 seconds (§6.1, §9).
- The email of an unverified user replaces its password hash and name, and
  Mailpit receives a new code that replaces the open one (§6.1).
- Within 60 seconds of the previous code for the same user, the sign-up
  changes nothing, sends no code, and the open code stays valid (§5, R-2).
- All branches return 202 with an identical body, and response times do not
  reveal the branch (§6.1, §9).
- A password shorter than 12 or longer than 128 code points returns 400
  `password_too_weak` as `application/problem+json` (§7, §9).
- Invalid input returns 422 `invalid_input` as `application/problem+json`,
  without echoing any submitted value (§7).
- No stored value holds the code or the password in the clear. No log record
  or `auth_events` row holds a password, code, or raw email (§9).
- A browser on an allowed origin can send a credentialed `POST` (§9).

## Evidence required

- The three sign-up branches, each with its stored state and email (§14).
- An identical response body across branches, and timings that do not separate
  them.
- The policy boundaries at 11, 12, 128, and 129 code points, counted in code
  points rather than bytes.
- The problem response shape and status for `password_too_weak`.
- The 60-second send interval at its boundary.

## Evidence recorded

All paths are under `apps/backend/`. The checks in `apps/backend/AGENTS.md`
pass: `alembic check`, Ruff, `ty`, and 84 tests at 97.5% coverage.

| Evidence                             | Where                                                                                                                                                                                                                                             |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Three branches, stored state, email  | `tests/integration/features/auth/presentation/http/test_sign_up_controller.py`: one test per branch against PostgreSQL and Mailpit                                                                                                                  |
| Identical body                       | The verified-branch test compares status, headers, and body with a new email's answer                                                                                                                                                            |
| Timing                               | Measured on uvicorn with the default 500 ms floor, n=30 per branch, shuffled order: medians 504.4 to 505.8 ms, p10 to p90 ranges overlapping. Without the floor the medians were 28 to 56 ms and separable. `test_an_accepted_sign_up_answers_no_sooner_than_the_minimum_response_time` guards the floor |
| Policy boundaries in code points     | `tests/unit/features/auth/domain/value_objects/test_password_policy.py`, with a 4-byte character                                                                                                                                                 |
| `password_too_weak` problem          | `test_a_password_outside_the_policy_answers_password_too_weak_as_a_problem`                                                                                                                                                                      |
| 60-second boundary                   | `tests/unit/features/auth/application/use_cases/test_sign_up_with_password_use_case.py` at 60 s and at 60 s minus 1 µs, for codes and for notices                                                                                              |
| Concurrent sign-ups                  | `tests/integration/features/auth/infrastructure/adapters/test_sql_user_repository.py`                                                                                                                                                           |
| Compose                              | The development container delivered a code to Mailpit through `mailpit:1025`                                                                                                                                                                     |

## Implementation notes

Decisions made while building, which the spec and ERD now record:

- **Timing.** Every branch hashes, mail leaves after the response through the
  request's background tasks, and the controller answers no sooner than
  `JSF_AUTH_SIGN_UP_MIN_RESPONSE_TIME` (500 ms). Hashing and background mail
  alone left a 5 to 13 ms gap between branches.
- **Unverified email within the interval changes nothing.** A security review
  showed that replacing the password without sending a new code lets an
  attacker's password ride on the code the mailbox owner already holds. The
  owner of the mailbox would then verify an account the attacker can sign in
  to. Inside the interval the earliest sign-up now wins. DEC-7 tracks both
  remaining orders: an attacker after the owner outside the interval, and an
  attacker who signs up first and repeats every 60 seconds. A person who
  resubmits within 60 seconds to fix a typo keeps the first password and
  resets it later.
- **Notice pacing.** The existing-account notice follows the same 60-second
  interval, so the endpoint cannot flood a verified user's inbox. Each notice
  writes one `auth_events` row of type `existing_account_notice_sent`, which
  also paces the next one.
- **Input.** An email whose NFKC form differs from itself, such as one with
  full-width letters, is refused with 422, because it would share an account
  with a different mailbox. Names refuse control characters, which PostgreSQL
  cannot store, and a password refuses a lone surrogate, which no hash can
  encode. `EmailStr` lower-cases the domain and drops a display name
  before `email` is stored.
- **422.** FastAPI's default body repeats each invalid input, which can be the
  whole body with its password. The app answers `invalid_input` with an
  `errors` list of `loc`, `msg`, and `type` instead.
- **Settings.** `AuthSettings` (`JSF_AUTH_*`) is separate from `AppSettings`,
  so a migration runs without the auth secrets. The app checks it at start-up.
  The SMTP values later moved to core's `AppSettings` as `JSF_SMTP_*`, with the shared
  `SmtpEmailSenderClient`. `smtp_security` is `none`, `starttls` (default), or
  `tls`, and `none` refuses SMTP credentials. `hide_input_in_errors` keeps a rejected secret out
  of the start-up error, and an empty variable counts as unset.
- **Ports added to §10's list.** `UnitOfWork` commits the shared session.
  `VerificationCodeGenerator` creates codes and `VerificationCodeHasher`
  computes their HMAC; they replaced the earlier `SecretGenerator` and
  `SecretHasher`, whose "secret" read like a password. `AuthEventRepository` records notices.
  Those two ports, `PasswordHasher`, and `Clock` later became helper functions
  (§10), because each is one operation with no state of its own.
- **Packages.** `pydantic[email]` resolved `email-validator` 2.3.0. Mailpit is
  `axllent/mailpit:v1.31.1`, pinned by digest.

## Implementation freedom

- How equal timing is achieved, for example hashing in every branch and
  sending mail after the response.
- Email wording and format, within §9's rules.
- Which `auth_events` types sign-up records. The spec names only
  `sign_in_failed` and `refresh_token_reused`.
- Backend limits on name length. The app enforces 1 to 100 characters (§11.2).
- Request field names, within `snake_case` (§7).
