# T-22: A social-only person sets a first password

- Status: blocked (DEC-4)
- Spec trace: §5 (recent authentication), §6.2 (a reset adds a password), §7
  `PUT /password` (first password), §9 (password policy)
- Blocked by: T-12, T-17, T-20, DEC-4
- Blocks: None

## Outcome

`PUT /v1/auth/password` without a current password adds a password to a user
who has none, inside the recent-authentication window.

## Context

- Setting a first password requires recent authentication; changing an
  existing one does not, because the current password is in the request (§5).
- A social-only user can already add a password through the reset link (T-10,
  §6.2).
- Social-only users exist from T-17 on.
- §6.2 states the session and notice effects only for changing an existing
  password. DEC-4 decides them for a first password.

## In scope

- The first-password path of `ChangePasswordUseCase` on
  `PUT /v1/auth/password`, answering 204.
- 403 `recent_authentication_required` outside the window (§5, §7).
- The §9 password policy that `PUT /password` already applies (R-8).
- The session and notice effects DEC-4 decides.

## Out of scope

- An app page (README).

## Acceptance

- A social-only user inside the window sets a password, gets 204, and can then
  sign in with it (§7).
- Outside the window, the request returns 403
  `recent_authentication_required` and changes nothing (§5, §7).
- A user who already has a password cannot skip the current password; the
  request returns 401 `invalid_credentials` (§7).
- DEC-4's session and notice effects hold.

## Evidence required

- Both sides of the window.
- A password user who omits the current password.
- DEC-4's effects.

## Implementation freedom

- Whether the first-password path is a branch of `ChangePasswordUseCase` or a
  sibling use case; §10 lists only `ChangePasswordUseCase`.
