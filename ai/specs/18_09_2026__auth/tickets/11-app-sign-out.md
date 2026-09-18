# T-11: A signed-in person signs out of the app

- Status: blocked (DEC-2)
- Spec trace: §5 (delivery by client kind), §7 `POST /sign-out`, §11.1
  (`sign_out_use_case.dart`, `clearTokens`)
- Blocked by: T-07, DEC-2
- Blocks: None

## Outcome

A signed-in person uses the sign-out control that DEC-2 places, the backend
session ends, and the app shows the sign-in page.

## Context

- §11.1 lists `sign_out_use_case.dart`, and T-06 provides `POST /sign-out`.
  No section says where the control lives or what it says.
- The web keeps the refresh token in a cookie; mobile keeps it in secure
  storage (§5).
- Until this ticket, the app signs out only when a refresh fails (T-07).

## In scope

- `SignOutUseCase`: `POST /v1/auth/sign-out` with the refresh token or the
  bearer token, then `clearTokens`, then `AuthSessionSignedOut`.
- The control and its string in `AuthStrings`, as DEC-2 specifies.

## Out of scope

- Revoking other devices; the API exists in T-13, and no page is specified.

## Acceptance

- Using the control ends the backend session: its refresh token then fails with
  `session_ended` (§5, §7).
- The router shows the sign-in page after sign-out (§11.1).
- On mobile, secure storage holds no tokens afterwards. On the web, the refresh
  cookie is cleared (§5).
- The control matches DEC-2.

## Evidence required

- The cubit's transition to signed out and the router redirect.
- Token removal from storage.
- A manual sign-out on iOS, Android, and the web.

## Implementation freedom

- Whether the use case sends the refresh token or the bearer token; §7 accepts
  either.
