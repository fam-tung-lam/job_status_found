# T-25: An Android person signs in with the native Google sheet

- Status: planned
- Spec trace: §3 (Android row), §4 (`google_sign_in` 7.2.0), §6.3, §7
  `POST /sign-in/{provider}/id-token`, §10 (`SignInWithIdTokenUseCase`, one
  verifier), §11.1 (provider choice), §12 (Android client), §14 (manual checks
  on real devices)
- Blocked by: T-18, T-19
- Blocks: None

## Outcome

On Android, "Continue with Google" opens the Credential Manager sheet instead
of the browser, and the chosen account lands signed in.

## Context

- The app sends the SHA-256 of a raw nonce to Google and the raw nonce to the
  backend. The backend accepts the ID token only when `SHA-256(raw nonce)`
  equals its `nonce` claim, so a stolen ID token alone cannot be replayed
  (§6.3).
- `google_sign_in` takes the nonce in `initialize()`, which runs once, so the
  Google nonce is per app start, not per attempt (§6.3).
- The accepted `aud` is the Google web client id (§6.3).
- `google_sign_in_android` 7.2.17 requires Flutter 3.44 or newer. `.fvmrc`
  pins Flutter 3.47.2 (read on 2026-09-18) (§4).
- iOS and the web keep the browser flow, and its backend contract does not
  change (§3).
- The endpoint promises every §6.5 failure, so it needs T-18's branches.

## In scope

- Backend: `SignInWithIdTokenUseCase` and
  `POST /v1/auth/sign-in/{provider}/id-token` with the ID token, the raw nonce,
  `client_kind`, and `remember_me`. It verifies through `OidcIdTokenVerifier`
  with the nonce mandatory, resolves the user through §6.5, and creates a
  session with `sign_in_method` `google`. Failures: 401
  `provider_token_invalid`, plus the §6.5 failures (§7, §10).
- App: `google_sign_in` 7.2.0 and `GoogleNativeCredentialClient`, which calls
  `initialize(serverClientId: <web client id>, nonce: ...)`, then
  `authenticate()`, then reads `account.authentication.idToken` (§4).
  `PlatformProviderCredentialSource` returns `ProviderIdTokenCredential` on
  Android (§11.1).
- The Google console "Android" client with the package name and signing SHA-1,
  in the same project as the web client, so Credential Manager works (§12).
  The project owner creates it (RISK-10).

## Out of scope

- iOS and the web, which keep the browser flow (§3).

## Acceptance

- On Android, the button opens the native sheet, and approving it signs the
  person in (§3, §6.3).
- iOS and the web still use the browser flow (§3).
- An ID token whose `nonce` is not the SHA-256 of the submitted raw nonce, or
  with a wrong `aud`, wrong `iss`, expiry, or a bad signature, returns 401
  `provider_token_invalid` (§6.3, §7).
- Every §6.5 outcome reachable through this endpoint matches the browser
  flow's (§6.5, §7).
- Closing the sheet returns the page to editing with no message (§11.2).

## Evidence required

- The endpoint's rejections, including the nonce hash check.
- Provider choice per platform.
- The Android cell of the platform table on a real device (§14).

## Implementation freedom

- Where the per-start raw nonce is kept in the app.
