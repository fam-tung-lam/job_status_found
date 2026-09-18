# T-26: A signed-in person changes their email address

- Status: blocked (DEC-6)
- Spec trace: §5 (recent authentication), §7 `POST /email-change/request`,
  `POST /email-change/confirm`, §9 (notice to the old address), §10
  (`RequestEmailChangeUseCase`, `ConfirmEmailChangeUseCase`), ERD
  (`change_email` challenge, `new_email`)
- Blocked by: T-20, DEC-6
- Blocks: None

## Outcome

A person requests a change to a new address, enters the 6-digit code sent to
that address, and the account's email becomes the new one. The old address
receives a notice.

## Context

- Changing the email requires recent authentication (§5).
- A `change_email` challenge is a 6-digit code looked up by
  `(user_id, purpose)`, with `new_email` set (ERD).
- §9 lists "email changed (to the old address)" among the notices.
- DEC-6 decides the taken-address response, the session effects, the code
  limits, and `email_verified_at`.

## In scope

- `RequestEmailChangeUseCase` and `POST /v1/auth/email-change/request`
  (Recent), answering 202 (§7).
- `ConfirmEmailChangeUseCase` and `POST /v1/auth/email-change/confirm`
  (Bearer), answering 204, with `verification_code_invalid` on failure (§7).
- The notice to the old address (§9, R-3).
- The behavior DEC-6 decides.

## Out of scope

- An app page (README).

## Acceptance

- Inside the window, a request creates a `change_email` challenge with
  `new_email`, sends a code to the new address, and returns 202. Outside it,
  the request returns 403 `recent_authentication_required` (§5, §7).
- The right code changes `email` and `email_normalized`, sends the notice to
  the old address, and returns 204 (§7, §9).
- A wrong code returns 400 `verification_code_invalid` (§7).
- DEC-6's outcomes hold.

## Evidence required

- Each outcome above, including DEC-6's cases.

## Implementation freedom

- Notice wording.
