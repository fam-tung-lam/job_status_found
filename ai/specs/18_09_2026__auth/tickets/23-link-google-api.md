# T-23: A signed-in person links a Google identity

- Status: blocked (DEC-5)
- Spec trace: §5 (recent authentication), §6.4 (Bearer attempt), §6.5 (purpose
  `link`), §7 `POST /oauth/{provider}/attempts` and `POST /oauth/exchange`
  with Bearer, `identity_already_linked`, §9 (notice "provider linked")
- Blocked by: T-17, T-20, DEC-5
- Blocks: None

## Outcome

A signed-in person runs the browser flow with purpose `link`, and the Google
identity attaches to their account.

## Context

- A `link` attempt is authenticated with the bearer token, which a browser
  navigation cannot send; that is why attempts start with a `POST` (§6.4).
- `initiating_user_id` is required for `link` (ERD).
- Purpose `link` requires that the identity belongs to no other user, and it
  ignores email matching (§6.5).
- `(user_id, provider)` is unique, so a user has at most one Google identity
  (ERD).
- §7 promises a `TokenPairResponse` from the exchange, and §6.4 shows it creating a
  session, which fits `sign_in` only. DEC-5 decides the `link` result.

## In scope

- Attempts with purpose `link`, authenticated with the bearer token and inside
  the recent-authentication window (§5, §7).
- At the callback: an identity owned by another user fails with
  `identity_already_linked` through the `error` redirect; otherwise the
  identity links to the initiating user, and the "provider linked" notice goes
  out (§6.4, §6.5, §9).
- The exchange result for `link`, as DEC-5 decides.
- The failure when the user already has a Google identity, as DEC-5 decides.

## Out of scope

- An app page (README).

## Acceptance

- A link attempt inside the window, approved at Google, links the identity to
  the initiating user and sends the notice (§6.5, §9).
- A Google identity that belongs to another user fails with
  `identity_already_linked`, delivered through the callback's `error`
  redirect, and nothing changes (§6.4, §6.5, §7).
- A Google account whose email differs from the user's still links (§6.5).
- Starting a link attempt outside the window returns 403
  `recent_authentication_required` (§5).
- The exchange's response and session effects match DEC-5.

## Evidence required

- Each outcome above.
- A manual link against Google (§14).

## Implementation freedom

- Whether the recent-authentication check runs at attempt start only or also
  at the exchange.
