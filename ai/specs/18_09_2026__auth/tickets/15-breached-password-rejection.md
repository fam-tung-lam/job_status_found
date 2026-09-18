# T-15: Passwords found in known breaches are rejected

- Status: planned
- Spec trace: §4 (`httpx2` moves to runtime), §6.2 (weak password leaves the
  reset token usable), §7 (`password_breached`), §9 (password policy, breach
  part), §10 (`BreachedPasswordChecker`)
- Blocked by: T-10, T-12
- Blocks: None

## Outcome

Sign-up, reset confirm, and password change reject a password that the Pwned
Passwords range API reports with `password_breached`, and accept it when the
API cannot be reached.

## Context

- The range API uses k-anonymity: only the first 5 SHA-1 hex characters leave
  the server (§9).
- The check fails open on an outage (§9).
- `httpx2` is already the project's test client and moves from `dev` to
  runtime here, its first runtime use (§4).
- The app already shows the `password_breached` inline message (T-08, T-10).

## In scope

- `BreachedPasswordChecker` port and a Pwned Passwords range adapter over
  `httpx2` 2.13.0 (§4, §10).
- The check wherever the §9 policy runs: `POST /sign-up`,
  `POST /password-reset/confirm`, and `PUT /password` (§7, R-8).

## Out of scope

- The first-password path (T-22), which inherits the policy.

## Acceptance

- A breached password returns 400 `password_breached` on each of the three
  endpoints (§7).
- The outbound request carries only the 5-character SHA-1 prefix (§9).
- With the API down or timing out, the password passes the breach check (§9).
- On reset confirm, a breached password leaves the link usable (§6.2).

## Evidence required

- A prefix-only request.
- Fail-open on an outage and on a timeout.
- The rejection on each endpoint.

## Implementation freedom

- The timeout and any response caching.
