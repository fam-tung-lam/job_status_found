# T-04: An access token authenticates requests and reads the signed-in user

- Status: implemented
- Spec trace: §5 (access token verification), §7 `GET /me` and the 401 rule,
  §8 rules 1, 2, and 4, §10 (auth guards, facade)
- Blocked by: T-03
- Blocks: T-06

## Outcome

`GET /v1/auth/me` with a valid bearer token returns the user, `has_password`,
and the linked providers. Without a valid token, it returns 401 with
`WWW-Authenticate: Bearer`.

## Context

- Verification follows RFC 8725: the algorithm is pinned to HS256, and `iss`,
  `aud`, `exp`, and `typ` are all required. It reads no table (§5).
- Any key in the ring verifies, so a key rotates without signing anyone out
  (§5).
- A revoked session, a suspended user, or a changed role keeps working on
  ordinary endpoints for up to 15 minutes. Only guards that load a row react
  immediately (§5).
- §8 rule 1 makes every feature router authenticated by default, so a new
  endpoint cannot be public by accident.

## In scope

- `AuthenticateAccessTokenUseCase`. The auth facade exports
  `AuthenticatedPrincipal`, `UserRole`, `AuthenticateAccessTokenUseCase`,
  and the guards below (§10).
- `features/auth/presentation/http/v1/guards/authentication_guards.py` with
  `get_authenticated_principal`, which returns
  `AuthenticatedPrincipal(user_id, session_id, role)` (§8 rule 2), and
  `require_role`, which loads the role from the database instead of trusting
  the claim (§8 rule 4).
- `app/app.py` includes every feature router with the principal dependency.
  Only `health` and the public `auth` endpoints opt out (§8 rule 1).
- `GetCurrentUserUseCase` and `GET /v1/auth/me` (§7).
- 401 responses carry `WWW-Authenticate: Bearer` (§7).

## Out of scope

- `require_recent_authentication` lands with its first consumer, T-20 (R-6).
- Refresh and sign-out (T-06).
- Any endpoint that uses `require_role`; none exists in this spec.

## Acceptance

- A valid access token on `GET /me` returns 200 with the user's profile
  fields, `has_password`, and the linked providers (§7).
- A missing, expired, or wrongly signed token returns 401
  `access_token_invalid` with `WWW-Authenticate: Bearer` (§5, §7).
- A token with a wrong `iss`, wrong `aud`, wrong `typ`, or an `alg` other than
  HS256, including `none`, returns 401 (§5).
- A token signed by a verify-only key in the ring is accepted; a token whose
  `kid` is not in the ring is rejected (§5).
- Verifying a token reads no table (§5).
- `GET /health` stays public, and a router included without an opt-out rejects
  anonymous requests (§8 rule 1).
- Handlers pass `principal.user_id` to use cases as an ordinary argument; use
  cases never see the token (§8 rule 2).
- `require_role` rejects a principal whose stored role differs from the
  required one, even when the token's `role` claim matches (§8 rule 4).

## Evidence required

- Each rejection case above.
- Key rotation: a token signed with key A still verifies after signing moves
  to key B and A becomes verify-only.
- Authenticated by default: an unmarked route rejects anonymous requests.
- `require_role` decides from the stored role, not the claim.

## Evidence recorded

All paths are under `apps/backend/`. The completed backend check passed 159
tests at 96.20% coverage, together with Ruff, `ty`, and the migration checks.

| Evidence | Where |
|----------|-------|
| JWT header and claim checks, `alg=none` rejection, missing claims, and verify-only key rotation | `tests/unit/features/auth/infrastructure/adapters/test_jwt_access_token_codec.py` |
| Authentication returns the principal without a database collaborator | `tests/unit/features/auth/application/use_cases/test_authenticate_access_token_use_case.py` |
| Wrongly signed and expired bearer tokens return 401 `access_token_invalid` with `WWW-Authenticate: Bearer` | `tests/integration/features/auth/presentation/http/v1/test_session_flow.py` |
| Current-user profile and a deleted token subject | `tests/unit/features/auth/application/use_cases/test_get_current_user_use_case.py` |
| Authenticated-by-default routing and public health/auth exceptions | `tests/integration/app/test_app.py` |
| Stored-role authorization | `tests/unit/features/auth/application/use_cases/test_require_user_role_use_case.py` |

## Implementation notes

- `GET /me` returns `id`, `email`, `first_name`, `last_name`, `avatar_url`,
  `locale`, `role`, `has_password`, and `linked_providers`.
- Every access-token verification failure maps to the one public code
  `access_token_invalid`. The 401 response carries
  `WWW-Authenticate: Bearer`.

## Implementation freedom

- How public endpoints express their opt-out.
- The failure `require_role` raises, since no endpoint uses it yet.
