# T-10: A person sets a new password from the reset link

- Status: planned
- Spec trace: §4 (`flutter_web_plugins`), §6.2 (reset confirm), §7
  `POST /password-reset/confirm`, §9 (notices), §11.1 (routing exception, web
  platform setup), §11.3 (reset-password page)
- Blocked by: T-09
- Blocks: T-15

## Outcome

Opening the emailed link shows the reset-password page. A valid new password is
saved, every session of the account ends, and the app opens the sign-in page
with "Your password was changed. Sign in with your new password."

## Context

- The token is checked before the password policy, so a too-weak password
  fails without consuming the token, and the person can try another password
  with the same link (§6.2).
- Confirming does not sign in. It revokes every session, including the one on
  the device that made the reset, so a stolen session cannot outlive the
  password it was opened with (§6.2).
- `ResetPasswordRoute` opens whether or not someone is signed in, because a
  reset link must work in a browser that still holds a session (§11.1).
- The link must be a path URL, `/reset-password?token=...`, not a `#` fragment
  (§4, §11.1).

## In scope

- Backend:
  - `ConfirmPasswordResetUseCase` and `POST /v1/auth/password-reset/confirm`,
    which answers 204.
  - An unknown, expired, used, or replaced token: 400 `reset_token_invalid`
    (§6.2).
  - A valid token with a password that fails the policy: 400
    `password_too_weak`, and the token stays unconsumed (§6.2).
  - Success: consume the challenge; store the new Argon2id hash, creating the
    credential for a social-only user; set `email_verified_at` if it was null;
    revoke every session with `password_changed`; send the "password changed"
    notice (§6.2, §9, R-3).
- App:
  - `usePathUrlStrategy()` in `main.dart` (§11.1).
  - `ResetPasswordPage` at `/reset-password?token=` with rows 1 to 6 of §11.3
    and `AutofillHints.newPassword` on the new-password field.
  - `ResetPasswordCubit` with `ResetPasswordEditing`,
    `ResetPasswordSubmitting`, `ResetPasswordRejected(failure)`,
    `ResetPasswordLinkInvalid`, and `ResetPasswordSucceeded`;
    `ConfirmPasswordResetUseCase` (§11.1).
  - The link-invalid state of §11.3, whose "Request a new link" opens
    `ForgotPasswordRoute`.
  - On 204, clear the stored tokens and open `SignInRoute` with the success
    `AppAlert`. `SignInRoute` takes an optional notice value, so the message
    survives the navigation (§11.3).
  - `ResetPasswordRoute` is exempt from the signed-in redirect (§11.1).

## Out of scope

- The breach check (T-15).
- Rewriting unknown paths to `index.html` and sending
  `Referrer-Policy: no-referrer` at the web host (§11.1). The repository holds
  no host configuration; the README tracks it as a deferred concern.

## Acceptance

- A valid token and a policy-compliant password return 204, replace the hash,
  and end every session of the user, including the requesting device's (§6.2).
- The same token then fails with `reset_token_invalid`, as do expired,
  unknown, and replaced tokens (§6.2).
- A too-short password with a valid token returns `password_too_weak`, and the
  same link then accepts a valid password (§6.2).
- A social-only user who confirms gains a password, and a user whose
  `email_verified_at` was null becomes verified (§6.2).
- The user receives the "password changed" notice (§9).
- Opened without `token`, the page shows the link-invalid state and sends no
  request (§11.3).
- `reset_token_invalid` shows the link-invalid state. `password_too_weak` and
  `password_breached` show the §11.2 inline messages, and the link stays
  usable (§11.3).
- On 204, the app clears its stored tokens and shows the success alert on the
  sign-in page (§11.3).
- A browser that holds a session opens the reset page instead of being
  redirected (§11.1).
- The web app's URLs have no `#` fragment (§11.1).

## Evidence required

- A weak password that leaves the reset token usable (§14).
- Revocation of every session of the user with `password_changed`.
- The reset page against the §11.3 behavior table, including the link-invalid
  state (§14).
- The router rule for a signed-in visitor opening a reset link (§14).
- A manual reset in a browser from the Mailpit link.

## Implementation freedom

- Whether the app validates the password length before sending (§11.3 requires
  12 to 128 characters) in the cubit or the form.
