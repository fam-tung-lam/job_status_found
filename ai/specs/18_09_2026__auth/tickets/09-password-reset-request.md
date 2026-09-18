# T-09: A person requests a password reset link from the forgot-password page

- Status: planned
- Spec trace: §2 (email links open the web app), §6.2 (reset request), §7
  `POST /password-reset/request`, §9 (enumeration, secrets), §11.2 ("Forgot
  your password?"), §11.3 (forgot-password page)
- Blocked by: T-07
- Blocks: T-10, T-14

## Outcome

From "Forgot your password?", a person submits an email, sees the "Check your
email" state, and an active account receives a reset link.

## Context

- The request endpoint never reveals whether an account exists. Its body is the
  same in every branch, and the email goes out after the response, so timing
  does not reveal the branch either (§6.2).
- "Blocked" means suspended or pending deletion (§6.2).
- The link always opens the web app, also for a person who uses the mobile
  app, because opening email links in the app is out of scope (§2, §6.2).
- A reset token is a 256-bit link token found by `secret_hash`, which has its
  own index (ERD).

## In scope

- Backend:
  - `RequestPasswordResetUseCase` and `POST /v1/auth/password-reset/request`,
    which answers 202.
  - An active user with no link sent in the last 60 seconds: replace the open
    `reset_password` challenge with a new 256-bit token, stored as an
    HMAC-SHA-256 `secret_hash` and valid for 30 minutes, then send
    `https://<web app>/reset-password?token=<token>` after the response (§6.2,
    §9).
  - An unknown email, a blocked user, or a link sent in the last 60 seconds:
    send nothing (§6.2).
  - A social-only user gets the same link (§6.2).
  - The email says the link expires in 30 minutes, and that a person who did
    not ask for it can ignore it and keep their password (§6.2).
  - Settings: the web app base URL, the link lifetime, and the send interval
    (§10).
- App:
  - "Forgot your password?" at the right end of the sign-in page's password
    label row, carrying the typed email (§11.2).
  - `ForgotPasswordPage` at `/forgot-password?email=` with rows 1 to 6 of
    §11.3, prefilled from `email`; "Back to sign in" carries the typed email
    to `SignInRoute`.
  - `ForgotPasswordCubit` with `ForgotPasswordEditing`,
    `ForgotPasswordSubmitting`, `ForgotPasswordRejected(failure)`, and
    `ForgotPasswordSent(email)`; `RequestPasswordResetUseCase` (§11.1).
  - The sent state of §11.3: headline "Check your email", the text with
    `{email}`, an outline "Resend link" button, and a ghost "Use a different
    email" button.
  - `ForgotPasswordRoute` opens while signed out.

## Out of scope

- Using the link (T-10).
- The reset-request IP throttle of 3 per 5 minutes (T-14).

## Acceptance

- Unknown, blocked, and active emails all get 202 with an identical body, and
  the response time does not depend on whether mail goes out (§6.2).
- Only an active account receives the link, and only when no link went out in
  the last 60 seconds (§6.2).
- A new request replaces the open challenge, so only the latest link works
  (§6.2).
- The stored challenge holds only the token's HMAC, and no log record holds
  the token or the raw email (§9).
- The app checks email syntax, shows the sent state after 202, and never says
  whether the account exists (§11.3).
- "Resend link" sends the same request again, stays disabled for 60 seconds
  after each send, and counts down ("Resend link in 42 s") (§11.3).
- "Use a different email" returns to editing with the email field focused
  (§11.3).
- Any other failure shows the §11.2 messages in an `AppAlert` above the
  primary button (§11.3).

## Evidence required

- The reset request branches (§14).
- The 60-second interval at its boundary.
- The forgot-password form against the §11.3 behavior table, including the
  resend countdown (§14).
- A manual request that delivers the link to Mailpit.

## Implementation freedom

- How mail is deferred until after the response.
- Email wording beyond the two statements §6.2 requires.
