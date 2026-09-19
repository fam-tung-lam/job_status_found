# T-08: A new visitor registers in the app and verifies the emailed code

- Status: implemented
- Spec trace: §5 (`remember_me`), §6.1, §11.1 (routing: `SignUpRoute`,
  `EmailVerificationRoute`), §11.2 (sign-up page, switch prompts, legal line,
  behavior, failure messages)
- Blocked by: T-07
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
- The verification page asks for the 6-digit code and the password that the
  person intends to bind to the account. Its route URL carries only the email;
  the password and remember choice are ephemeral route state.

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
  `ConfirmEmailVerificationUseCase`, and resend. The page shows "Check your
  email", an explanation, code and password fields, "Verify", a resend
  control with a 60-second countdown, and a control to use another email.
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
  browser (§11.2).
- "Register" and "Log in" move between the two pages and keep the typed email
  (§11.2).
- Signing in with an unverified account opens the verification page with the
  email (§11.2).
- The right code and matching password sign the person in, and the router
  leaves the auth pages. A web sign-up's session is not persistent (§5).
- The verification page shows the specified content and the generic
  verification failure message. Every control is disabled in flight.
- The 60-second resend countdown starts on page entry and after an accepted
  resend. An accepted resend clears the code and keeps the password.
- The URL contains only the email. A direct visit or web reload asks for the
  password again. Sign-in keeps its `remember_me` choice; sign-up and direct
  visits use the platform default: false on web and true on mobile.
- Autofill uses `givenName`, `familyName`, `email`, and `newPassword`, and the
  layout, keyboard, and accessibility rules of §11.2 hold.

## Evidence required

- The sign-up form against the §11.2 behavior table (§14).
- The verification page behavior above.
- Registration through pages with real repositories and use cases (§14).
- A manual registration on iOS, Android, and the web, using the code from
  Mailpit.

## Evidence recorded

All paths are under `apps/frontend/`. `fvm flutter analyze`, the formatting
check, 40 automated tests, and the debug web build pass.

| Evidence | Where |
|----------|-------|
| Sign-up validation and password-failure behavior | `test/widget/features/auth/presentation/widgets/email_sign_up_form_test.dart` |
| Registration reaches verification through real frontend layers | `test/integration/features/auth/presentation/pages/sign_up_page_test.dart` |
| Required code/password validation, single-flight resend, full-page lock, and code clearing only after success | `test/widget/features/auth/presentation/pages/email_verification_page_test.dart` |
| Direct verification and sign-up routes survive restoration | `test/integration/app/app_router_test.dart` |

Open evidence: manual registration on iOS, Android, and web against the Compose
backend, using the Mailpit code, has not been run.

## Implementation notes

- `url_launcher` 6.3.2 is a direct dependency for the configured Terms of Use
  and Privacy Policy URLs.
- The password and remember choice never enter the URL or persistent route
  state. The route keeps them only in memory, and a direct visit or reload
  requires the password again.
- Resend is single-flight. While confirmation or resend is in flight, all
  fields and navigation controls are disabled.

## Implementation freedom

- How the email travels to `EmailVerificationRoute`.
- How `AppSettings` reads the two legal URLs.
