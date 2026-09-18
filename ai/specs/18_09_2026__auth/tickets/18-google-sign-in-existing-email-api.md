# T-18: A Google sign-in whose email already has an account links safely or refuses

- Status: planned
- Spec trace: D-5, §6.5 (email-taken branches), §7 (409 mapping), §9 (notice
  "provider linked")
- Blocked by: T-17
- Blocks: T-25

## Outcome

When a new Google identity's email already belongs to a user, sign-in follows
§6.5: it links the identity and emails a notice, takes over an unverified
account, or fails with `account_exists_link_required`.

## Context

- An existing account is linked by email only when both sides have verified
  that email. This blocks the pre-hijacking account takeover class (D-5).
- "Authoritative" means the provider vouches for the mailbox today. Google
  does when the address ends in `@gmail.com` or the `hd` claim is set with
  `email_verified` true, which is Google's own rule (§6.5).
- The take-over branch is the pre-hijacking defence. An unverified account was
  created by someone who never proved the mailbox, so its password is
  discarded when the real owner arrives through an authoritative provider
  (§6.5).
- `account_exists_link_required` tells the person to sign in the way they did
  before and link the provider under account settings (§6.5). No
  account-settings page is specified yet (README).

## In scope

- The email-taken branches of `ResolveProviderIdentityUseCase` for purpose
  `sign_in`, matched by `email_normalized` (§6.5):
  - provider not authoritative for the email: 409
    `account_exists_link_required`;
  - authoritative, existing user verified: link the identity, email the
    "provider linked" notice, and sign in;
  - authoritative, existing user unverified: delete its password credential
    and challenges, mark it verified, link the identity, and sign in.
- The "provider linked" notice (§9, R-3).

## Out of scope

- Purpose `link` (T-23).

## Acceptance

- A non-authoritative email match returns 409
  `account_exists_link_required`, and nothing is linked or changed (§6.5, §7).
- An authoritative match on a verified user links the identity, sends the
  notice, and completes sign-in (§6.5, §9).
- An authoritative match on an unverified user removes its password credential
  and open challenges, sets `email_verified_at`, links the identity, and
  completes sign-in. The old password no longer signs in (§6.5).
- A returning `(provider, sub)` never reaches these branches (§6.5).

## Evidence required

- Each email-taken branch of §6.5, including the authoritative rule for an
  `@gmail.com` address and for the `hd` claim (§14).
- The pre-hijacking case end to end: an unverified password sign-up by one
  party, then the mailbox owner's Google sign-in, after which the first
  party's password fails.

## Implementation freedom

- Notice wording.
