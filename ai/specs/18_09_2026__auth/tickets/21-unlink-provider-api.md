# T-21: A person unlinks Google while keeping a way to sign in

- Status: planned
- Spec trace: §5 (recent authentication), §7 `DELETE /identities/{provider}`,
  §8 rule 3 (ownership in the query), ERD (at least one sign-in method)
- Blocked by: T-17, T-20
- Blocks: None

## Outcome

`DELETE /v1/auth/identities/google` removes the person's Google identity,
unless it is their last way to sign in.

## Context

- A user always has a password credential, an external identity, or both
  (ERD).
- The ERD also names a "remove-password use case" as an enforcer, but the spec
  neither lists nor exposes one, so this ticket is the only enforcer (README).
- An identity the principal does not have is not found by an owner-filtered
  query, so it is a 404 (§8 rule 3).
- No app page is specified for this; the result is visible through the API.

## In scope

- `UnlinkExternalIdentityUseCase` and `DELETE /v1/auth/identities/{provider}`
  (Recent), answering 204 (§7).
- 409 `last_sign_in_method` when the user has no password credential and no
  other identity (§7).
- 404 for a provider the principal has not linked (§8 rule 3).

## Out of scope

- Linking (T-23).

## Acceptance

- A user with a password and a linked Google identity unlinks it: 204, and
  the `external_identities` row is gone (§7).
- A social-only user whose only method is this identity gets 409
  `last_sign_in_method`, and nothing is removed (§7).
- Outside the 10-minute window, the request returns 403
  `recent_authentication_required` (§5).
- Unlinking a provider the principal has not linked returns 404 (§8 rule 3).

## Evidence required

- Each outcome above, including the last-method rule.

## Implementation freedom

- None: §7 and §8 rule 3 fix every outcome.
