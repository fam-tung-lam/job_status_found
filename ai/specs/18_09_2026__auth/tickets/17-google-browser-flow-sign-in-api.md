# T-17: A person signs in with Google through the browser flow

- Status: planned
- Spec trace: D-5, D-7, §3 (browser flow), §4 (`authlib`, `pyjwt`), §6.4, §6.5
  (purpose `sign_in` without an email match), §7
  `POST /oauth/{provider}/attempts`, `GET, POST /oauth/{provider}/callback`,
  `POST /oauth/exchange`, §9 (exchange throttle, secrets), §10 (one verifier,
  settings), §12 (web client), §15 (Google PKCE)
- Blocked by: T-14
- Blocks: T-18, T-19, T-21, T-22, T-23, T-24

## Outcome

An API client starts an attempt, the person approves at Google, the callback
redirects to the app's redirect URI with a one-time code, and exchanging that
code with the PKCE verifier returns a `TokenPair` for a new or returning Google
user.

## Context

- The app asks for an attempt with a `POST`, so the body can carry the PKCE
  challenge (§6.4).
- Tokens never travel in a redirect URL. The redirect carries a 60-second
  one-time code that is useless without the PKCE verifier only the app holds,
  which defeats a malicious Android app on the same custom scheme (§6.4).
- State lives in `oauth_authorization_attempts`, not a cookie. Each step
  requires the previous instant set and its own null, which makes every `state`
  and exchange code single-use (§6.4, ERD).
- A returning social user is found by `(provider, sub)` only, never by email
  (D-5, §6.5).
- Only Authlib's `AsyncOAuth2Client` is used, not its Starlette integration
  (§4).
- Until T-18, an email that already belongs to a user fails with
  `account_exists_link_required` (R-7).

## In scope

- `OidcIdTokenVerifier`, configured per provider with issuers, JWKS URL,
  audience allow-list, and a mandatory-nonce flag. It fetches JWKS with
  `httpx2`, caches it for an hour, refetches once on an unknown `kid`, and pins
  `RS256` (§10). For Google: `iss` `https://accounts.google.com` or
  `accounts.google.com`, and `aud` the web client id (§6.3, §6.4).
- `AuthorizationCodeClient` on `authlib` 1.8.0 `AsyncOAuth2Client`:
  authorization URL, PKCE S256 toward Google, and the token request with the
  client secret. Send PKCE, and drop it if Google rejects it (§4, §15).
- `StartOAuthAuthorizationUseCase` and `POST /oauth/{provider}/attempts` for
  purpose `sign_in`: `client_kind`, `client_redirect_uri` exactly on the
  allow-list, and `client_code_challenge` (S256). It stores the attempt with
  `state_hash`, `nonce`, and `provider_code_verifier`, valid for 10 minutes,
  and answers 201 with `authorization_url` (§6.4, §7).
- 400 `redirect_uri_not_allowed`, and 400 `provider_not_configured` for a
  provider with no client id (§7, §10).
- `CompleteOAuthCallbackUseCase` and `GET, POST /oauth/{provider}/callback`:
  claim the attempt by `state_hash`, exchange the code, verify the ID token
  and nonce, resolve the user, store `exchange_code_hash`, and answer 303 to
  `client_redirect_uri` with the one-time code, or with `error=<code>` on any
  failure (§6.4, §7).
- `ResolveProviderIdentityUseCase` for purpose `sign_in` (§6.5):
  - `(provider, sub)` already linked: sign in that user, or fail with
    `account_unavailable` when the user is suspended or pending deletion;
  - no email claim: `provider_email_missing`;
  - email not taken, provider says verified: create a verified user and link
    the identity;
  - email not taken, provider says unverified: create an unverified user, link
    the identity, send a code, and fail with `email_verification_required`;
  - email taken: `account_exists_link_required` until T-18 (R-7).
- `ExchangeOAuthCodeUseCase` and `POST /oauth/exchange` with the one-time code,
  the PKCE verifier, and `remember_me`. It checks the verifier against
  `client_code_challenge`, honors the 60-second lifetime, consumes the attempt,
  and creates a session with `sign_in_method` `google` and the attempt's
  `client_kind`. Failure: 400 `exchange_code_invalid` (§5, §6.4, §7).
- The exchange IP throttle, 20/min, on T-14's throttle (§9).
- On each sign-in, `external_identities.email`, `email_verified`, and
  `last_signed_in_at` are updated. A created user gets `avatar_url` from the
  `picture` claim (ERD).
- Provider tokens are discarded after the ID token is verified (D-7).
- Settings: Google client id and secret as `SecretStr`, the client redirect
  allow-list (`com.ptlam.jobstatusfound:/oauth-callback` and
  `https://<web app>/auth.html`), and the attempt and exchange-code lifetimes
  (§5, §6.4, §10).
- The Google console "Web application" client with redirect URI
  `https://<api>/v1/auth/oauth/google/callback` (§12). The project owner
  creates it (RISK-10).

## Out of scope

- Emails that already belong to a user (T-18).
- Purposes `link` and `reauthenticate` (T-23, T-24).
- The app side (T-19) and the native ID-token endpoint (T-25).

## Acceptance

- A valid attempt returns 201 with an `authorization_url` that carries
  `state`, `nonce`, and a PKCE S256 challenge toward Google (§6.4).
- A `client_redirect_uri` that is not exactly on the allow-list returns
  `redirect_uri_not_allowed`. A provider with no client id returns
  `provider_not_configured` (§7, §10).
- A callback for an expired or already-used attempt redirects to the app with
  `error=<code>` and never with a token (§6.4).
- The ID token is rejected for a wrong `iss`, a wrong `aud`, expiry, a wrong
  nonce, an unknown `kid` after one refetch, and `alg=none` (§14).
- A returning `(provider, sub)` signs in its user without reading the email
  claim. A blocked user gets `account_unavailable` (§6.5).
- A token without an email claim gets `provider_email_missing` (§6.5).
- A new, provider-verified email creates a verified user with a linked
  identity (§6.5).
- A new, unverified email creates an unverified user, links the identity,
  sends a code, and fails with `email_verification_required` (§6.5).
- An email that already belongs to a user fails with
  `account_exists_link_required` and changes nothing (R-7).
- The exchange returns a `TokenPair` per `client_kind` only for the matching
  PKCE verifier, once, within 60 seconds. Anything else returns
  `exchange_code_invalid` (§6.4, §7).
- No provider access or refresh token is stored, and `state` and exchange codes
  are stored as SHA-256 (D-7, §9).
- The exchange returns 429 after 20 requests per minute from one IP (§9).

## Evidence required

- The verifier against tokens signed by a test RSA key with a stubbed JWKS
  response: wrong `iss`, wrong `aud`, expired, wrong nonce, unknown `kid`, and
  `alg=none` (§14).
- Each §6.5 branch this ticket owns (§14).
- Single use of `state` and the exchange code, and both lifetimes at their
  boundaries (§14).
- A manual sign-in against Google with a real web client (§14).

## Implementation freedom

- The response to a callback whose `state` matches no attempt; there is no app
  redirect URI to return to.
- Callback `error` values beyond the §7 codes.
- Where the JWKS cache lives.
