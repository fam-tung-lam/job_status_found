# T-08: A new visitor registers in the app and verifies the emailed code

- Status: blocked (DEC-1)
- Spec trace: §5 (`remember_me`), §6.1, §11.1 (routing: `SignUpRoute`,
  `EmailVerificationRoute`), §11.2 (sign-up page, switch prompts, legal line,
  behavior, failure messages)
- Blocked by: T-07, DEC-1
- Blocks: T-19

## Outcome

A visitor fills the sign-up page, enters the 6-digit code from the email on the
verification page, and lands signed in on the home page.

## Context

- Sign-up answers 202 in every case, and the app then opens
  `EmailVerificationRoute` with the email (§11.2).
- Sign-in's `email_verification_required` also opens `EmailVerificationRoute`;
  the backend has already sent a fresh code (§11.2).
- The sign-up page has no "Remember this device" checkbox, so a web sign-up is
  not persistent. iOS and Android send `remember_me: true` (§5).
- §11.1 names `email_verification_page`, `email_verification_cubit`, and
  `confirm_email_verification_use_case.dart`, but neither §11.2 nor §11.3
  specifies the verification page. DEC-1 supplies it.

## In scope

- `SignUpPage` at `/sign-up` built from `AuthPageFrame` and `EmailSignUpForm`:
  rows 1 to 3, 5 to 8, and 10 to 12 of §11.2. Row 4 stays hidden until T-19
  (R-4).
- The legal line "By signing up you agree to our Terms of Use and Privacy
  Policy." with both names opening `AppSettings.termsUrl` and
  `AppSettings.privacyUrl` in the browser through `url_launcher`. Both
  `AppSettings` values are new (§11.2).
- `AuthSwitchPrompt` on both pages: "Don't have an account? Register." and
  "Already have an account? Log in.", each carrying a typed email as a query
  parameter (§11.2).
- `SignUpFormCubit` and `SignUpWithPasswordUseCase`. Validation: both names
  not empty and at most 100 characters, email syntax, and a password of 12 to
  128 characters (§11.2).
- The name fields share a row and stack when the column is narrower than 320
  logical pixels (§11.2).
- `password_too_weak` and `password_breached` inline under the password field
  (§11.2).
- `EmailVerificationPage`, `EmailVerificationCubit`,
  `ConfirmEmailVerificationUseCase`, and resend, as DEC-1 specifies.
- `SignInFormEmailVerificationRequired(email)` opens `EmailVerificationRoute`
  (§11.2).
- A confirmed code stores the token pair and emits `AuthSessionSignedIn`.

## Out of scope

- The Google button and the `provider_*` messages (T-19).

## Acceptance

- Every valid sign-up opens `EmailVerificationRoute` with the email, whether
  or not the email already had an account (§6.1, §11.2).
- The first submit with invalid fields shows inline messages and sends no
  request (§11.2).
- `password_too_weak` shows "Use at least 12 characters." and
  `password_breached` shows "This password appears in known data breaches.
  Choose another." under the password field (§11.2).
- "Terms of Use" and "Privacy Policy" open their configured URLs in the
  browser, and the app sends no terms version (§11.2).
- "Register" and "Log in" move between the two pages and keep the typed email
  (§11.2).
- Signing in with an unverified account opens the verification page with the
  email (§11.2).
- The right code signs the person in, and the router leaves the auth pages. A
  web sign-up's session is not persistent (§5).
- The verification page shows DEC-1's content and messages.
- Autofill uses `givenName`, `familyName`, `email`, and `newPassword`, and the
  layout, keyboard, and accessibility rules of §11.2 hold.

## Evidence required

- The sign-up form against the §11.2 behavior table (§14).
- The verification page against DEC-1's behavior.
- Registration through pages with real repositories and use cases (§14).
- A manual registration on iOS, Android, and the web, using the code from
  Mailpit.

## Implementation freedom

- How the email travels to `EmailVerificationRoute`.
- How `AppSettings` reads the two legal URLs.
