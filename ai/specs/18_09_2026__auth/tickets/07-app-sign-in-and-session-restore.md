# T-07: A verified person signs in on the app and stays signed in

- Status: implemented
- Spec trace: D-3, §5 (delivery by client kind, `remember_me`), §11.1 (HTTP
  client package, token storage, state names, routing), §11.2 (sign-in page,
  design system additions, layout, behavior, failure messages, accessibility),
  §13 (Phase 1), §14 (frontend)
- Blocked by: T-05, T-06
- Blocks: T-08, T-09, T-11

## Outcome

A signed-out visitor lands on the sign-in page at `/sign-in`. A verified person
signs in on iOS, Android, or the web, reaches the home page, and stays signed
in after a reload or an app restart.

## Context

- The app has one route, `HomeRoute`, and `JobStatusFoundHttpClient` offers
  only `get` and `close`.
- Only `lib/packages/job_status_found_http_client/` may import `dio`, and
  `fresh_dio` stays private to it too (frontend `AGENTS.md`, §11.1).
- The web app keeps the access token in memory and relies on the `HttpOnly`
  refresh cookie. Mobile apps keep both tokens in `flutter_secure_storage`
  (§5).
- The mock-up decides what is on the page and its wording. The design system
  decides the look (§11.2).
- Accounts to sign in with come from the API today (T-02, T-03). The app's
  registration arrives with T-08.

## In scope

- HTTP client package (§11.1):
  - `post`, `put`, and `delete`; `setTokens`, `clearTokens`, and an
    `authenticationStatus` stream;
  - `fresh_dio` 0.6.0 attaches the bearer token, refreshes on 401 or 30
    seconds before expiry, single-flights concurrent refreshes, retries once,
    and signals sign-out when refresh fails; the refresh call uses a second
    `Dio`;
  - a `TokenStorage` from `app/di.dart`: `flutter_secure_storage` on mobile,
    memory on the web;
  - on the web, `BrowserHttpClientAdapter(withCredentials: true)` behind a
    conditional import, so mobile builds still compile;
  - the sealed exception exposes the problem `code` and `Retry-After`, because
    the app switches on `code`, never on `detail` (§7).
- Design system: `AppTextField` (label above the field, placeholder, helper
  text, error text, optional action at the end of the label row, optional
  obscure toggle), `AppLabeledDivider`, `AppSizes.controlXxl` = 48, and
  `AppSizes.formMaxWidth` = 400, each with a preview in `src/previews/` and a
  test (§11.2).
- The auth feature skeleton of §11.1 with `pushAuthFeatureScope`.
- `AuthSessionCubit` with `AuthSessionRestoring`, `AuthSessionSignedOut`, and
  `AuthSessionSignedIn(user)`, and `RestoreSessionUseCase`: the web restores
  through the refresh cookie, mobile from stored tokens, and the user comes
  from `GET /me` (§5, §11.1).
- Routing: `createAppRouter` takes `AuthSessionCubit`, its stream feeds
  `refreshListenable`, and `redirect` sends a signed-out visitor to
  `SignInRoute` and a signed-in one away from the auth pages.
  `AuthSessionRestoring` shows `AppSpinner` (§11.1).
- `SignInPage` at `/sign-in` built from `AuthPageFrame` and `EmailSignInForm`:
  rows 1 to 3, 5, 7 to 9, and 11 of §11.2. Row 4 stays hidden until T-19
  (§13, R-4).
- Row 9, "Remember this device", on the web only: unchecked by default, with
  the help tooltip "Stay signed in on this device for 30 days. Do not use on a
  shared computer." iOS and Android hide it and send `remember_me: true` (§5,
  §11.2).
- `SignInFormCubit` with `SignInFormEditing`, `SignInFormSubmitting`,
  `SignInFormRejected(failure)`, and
  `SignInFormEmailVerificationRequired(email)`; `SignInWithPasswordUseCase`
  (§11.1).
- The §11.2 behavior rows that apply to sign-in, and the messages for
  `invalid_credentials`, `too_many_attempts`, `account_unavailable`, and no
  connection, timeout, or 5xx.
- `AuthStrings` through `AppStrings`, and `AppStrings.appWordmark` "JSV".
  `appTitle` stays the window and task-switcher title (§11.2).
- The layout, autofill, keyboard, and accessibility rules of §11.2.

## Out of scope

- Row 12 and the switch prompts (T-08).
- "Forgot your password?" (T-09).
- The Google button, row 4 (T-19).
- Opening `EmailVerificationRoute` on `email_verification_required` (T-08).
- A sign-out control (T-11).

## Acceptance

- Opening any app page while signed out shows `SignInPage` at `/sign-in`.
  While the session restores, the spinner shows instead, so a reload never
  flashes the sign-in page (§11.1).
- A verified person who submits the right email and password reaches the home
  page, and `TextInput.finishAutofillContext()` runs so the password manager
  offers to save (§11.2).
- After a web reload the session restores through the refresh cookie; after a
  mobile restart, from secure storage (§5, §11.1).
- A signed-in visitor opening `/sign-in` is sent away from it (§11.1).
- When refresh fails, the app returns to the sign-in page (§11.1).
- The web shows "Remember this device" unchecked and sends its state as
  `remember_me`. iOS and Android hide it and send `true` (§5, §11.2).
- The first submit with invalid fields shows an inline message under each
  invalid field and sends no request; afterwards, a field revalidates as it
  changes. Sign-in checks only email syntax and a non-empty password (§11.2).
- While a request is in flight, the primary button shows `AppSpinner` and
  every button and field is disabled (§11.2).
- Each sign-in failure `code` shows its §11.2 message in an `AppAlert` above
  the primary button; the password field clears and the email stays.
  `too_many_attempts` shows the minutes from `Retry-After` (§11.2).
- The page contains no color, radius, text style, or padding literal. It works
  in both themes, survives a 200% text scale without clipping, and every
  interactive element is at least 48 by 48 logical pixels (§11.2).
- `dio` and `fresh_dio` are imported only inside the HTTP client package
  (§11.1).

## Evidence required

- Each new design system component and its preview (§11.2).
- The sign-in form against the §11.2 behavior table: inline validation, the
  disabled state in flight, the message per failure `code`, and the web-only
  checkbox (§14).
- The session cubit's transitions and the DTO round trips (§14).
- One router check per redirect rule (§14).
- The page working through real repositories and use cases (§14).
- A manual sign-in on iOS, Android, and the web against the Compose backend,
  including a web reload and a mobile restart.

## Evidence recorded

All paths are under `apps/frontend/`. `fvm flutter analyze`, the formatting
check, 40 automated tests, and the debug web build pass.

| Evidence | Where |
|----------|-------|
| Web remember choice, mobile persistence default, validation, disabled in-flight state, and failure messages | `test/widget/features/auth/presentation/widgets/email_sign_in_form_test.dart` |
| Session restore and reaction to token revocation | `test/unit/features/auth/presentation/bloc/auth_session_cubit_test.dart` |
| Mobile tokens survive a storage-adapter restart | `test/unit/packages/job_status_found_http_client/src/job_status_found_token_storage_test.dart` |
| Bearer attachment, single refresh, and protected-request retry | `test/integration/packages/job_status_found_http_client/src/dio_job_status_found_http_client_test.dart` |
| Signed-out, signed-in, restoration, direct sign-up, and direct verification routing | `test/integration/app/app_router_test.dart` |

Open evidence: manual sign-in on iOS, Android, and web against the Compose
backend, including a web reload and mobile restart, has not been run.

## Implementation notes

- The HTTP client owns token attachment, refresh, retry, cookie credentials,
  and platform-specific token storage. The auth feature sees only its public
  client abstraction.
- Router restoration preserves a requested auth location instead of replacing
  it with `/sign-in`; a signed-in state still redirects away from auth pages.
- User-visible auth text is routed through the localization abstraction.

## Implementation freedom

- How the HTTP client reads the refresh token per platform.
- `AuthPageFrame` internals, as long as it renders rows 1 to 3 and the centered
  column and builds no `Scaffold` (§11.2).
- The shape of `current_user_dto.dart`, matching T-04's response.
