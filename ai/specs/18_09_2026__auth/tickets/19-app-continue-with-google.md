# T-19: A person continues with Google in the app on the web, iOS, and Android

- Status: blocked (DEC-3)
- Spec trace: §3 (platform table, browser flow), §4 (`flutter_web_auth_2`,
  `crypto`), §6.4 (app side), §11.1 (provider choice, platform setup), §11.2
  (row 4, `AppProviderSignInButton`, brand mark, behavior, failure messages),
  §14 (manual checks), §15 (legal line)
- Blocked by: T-08, T-17, DEC-3
- Blocks: T-25

## Outcome

Tapping "Continue with Google" on the sign-in or sign-up page runs the browser
flow on the web, iOS, and Android, and the person lands signed in.

## Context

- The web uses the browser flow because `google_sign_in` on the web cannot
  sign in from a custom button. iOS uses it because the Google iOS SDK opens
  the same system browser session (§3).
- Delivery can start with the browser flow everywhere; T-25 adds the Android
  native sheet without changing the backend contract (§3, R-10).
- On the web, `flutter_web_auth_2` needs `web/auth.html` on the app's origin
  (§4).
- Google requires its standard multicolor "G" on a neutral background; an
  outlined button satisfies it (§11.2).
- DEC-3 decides whether the sign-in page shows the legal line under the Google
  button, because that button can also create an account (§15).

## In scope

- `AppProviderSignInButton`: outlined, full width, brand mark, centered label,
  taking an `AppIdentityProvider` value. The Google mark is a PNG at 1x, 2x,
  and 3x in the design system folder, declared in `pubspec.yaml`. Preview and
  test (§11.2, R-5).
- `ProviderSignInButtons` shows row 4 on both pages (§11.2).
- `flutter_web_auth_2` 5.1.0 and `crypto`. `BrowserAuthorizationClient`
  creates the PKCE verifier and S256 challenge, calls
  `POST /oauth/{provider}/attempts`, opens the URL, reads `code` or `error`
  from the callback, and calls `POST /oauth/exchange` with the verifier and
  `remember_me` (§4, §6.4).
- `PlatformProviderCredentialSource` returns `ProviderExchangeCodeCredential`
  on every platform for now. `ProviderCredential` is sealed, and
  `SignInWithProviderUseCase` sends it to the matching endpoint, so pages and
  cubits never branch on platform (§11.1).
- Platform setup (§11.1):
  - iOS: the custom scheme in `Info.plist`;
  - Android: `com.linusu.flutter_web_auth_2.CallbackActivity` with the custom
    scheme in the manifest, and the main activity stays `singleTop`;
  - web: `web/auth.html` from the `flutter_web_auth_2` README.
- Behavior (§11.2):
  - a closed sheet or browser, or the 300-second timeout, returns the page to
    editing with no message;
  - `email_verification_required` opens `EmailVerificationRoute`;
  - the messages for `account_exists_link_required`, `provider_email_missing`,
    `provider_token_invalid`, `exchange_code_invalid`,
    `provider_not_configured`, a callback `error`, and the shared codes.
- The sign-in page's legal line, as DEC-3 decides.

## Out of scope

- The Android native sheet (T-25).
- Linking from account settings; no page is specified (README).

## Acceptance

- On the web, iOS, and Android, "Continue with Google" completes the browser
  flow, and the router leaves the auth pages (§3, §6.4).
- Closing the browser, or the 300-second timeout, returns the page to editing
  with no message (§11.2).
- Each provider failure `code` shows its §11.2 message, and
  `email_verification_required` opens the verification page (§11.2).
- While the flow runs, every button and field on the page is disabled (§11.2).
- The button shows the Google mark in its brand colors in both themes (§11.2).
- The sign-in page matches DEC-3.

## Evidence required

- The new component and its preview (§11.2).
- The provider flow through pages with real repositories and use cases (§14).
- The manual browser-flow cells of the platform table on the web and iOS, and
  on Android until T-25 (§14).

## Implementation freedom

- How the PKCE verifier is kept between the attempt and the exchange.
