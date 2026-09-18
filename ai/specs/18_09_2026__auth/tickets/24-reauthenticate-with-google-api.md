# T-24: A signed-in person re-authenticates with Google

- Status: blocked (DEC-5)
- Spec trace: §5 (recent authentication), §6.4 (Bearer attempt), §6.5 (purpose
  `reauthenticate`), §7 `POST /oauth/{provider}/attempts` and
  `POST /oauth/exchange` with Bearer
- Blocked by: T-17, T-20, DEC-5
- Blocks: None

## Outcome

A signed-in person runs the browser flow with purpose `reauthenticate` and
reopens the recent-authentication window without a password.

## Context

- When the window has closed, the app asks for the password, or runs a
  provider flow with purpose `reauthenticate` (§5). Social-only users have
  only the provider flow.
- Purpose `reauthenticate` requires that the identity belongs to the
  initiating user (§6.5).
- `initiating_user_id` is required for `reauthenticate` (ERD).
- DEC-5 decides what the exchange returns, which session it refreshes, and the
  failure for an identity that belongs to someone else or to nobody.

## In scope

- Attempts with purpose `reauthenticate`, authenticated with the bearer token
  (§6.4, §7).
- At the callback: the identity must belong to the initiating user; the
  failure otherwise, as DEC-5 decides (§6.5).
- The exchange result for `reauthenticate`, as DEC-5 decides.

## Out of scope

- Password re-authentication (T-20).
- An app page (README).

## Acceptance

- After a successful `reauthenticate` flow, a Recent endpoint such as
  `DELETE /me` succeeds for 10 minutes (§5).
- A Google identity of another user, or one linked to nobody, fails as DEC-5
  decides, and the window stays closed (§6.5).

## Evidence required

- Each outcome above.
- A manual re-authentication against Google (§14).

## Implementation freedom

- None beyond what DEC-5 leaves open.
