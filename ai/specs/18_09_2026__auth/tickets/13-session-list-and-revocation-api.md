# T-13: A signed-in person lists and revokes their sessions

- Status: planned
- Spec trace: §7 `GET /sessions`, `DELETE /sessions/{session_id}`, §8 rule 3
  (ownership in the query), §9 (secrets), §10 (`sessions_controller.py`), ERD
  (`sessions` index, `revoked_by_user`)
- Blocked by: T-06
- Blocks: None

## Outcome

`GET /v1/auth/sessions` lists the person's sessions, and
`DELETE /v1/auth/sessions/{session_id}` ends one of them.

## Context

- A session is one sign-in on one device (ERD).
- Index `sessions (user_id) WHERE revoked_at IS NULL` serves the list (ERD).
- Every repository method that touches user data takes `owner_id`, and the SQL
  filters by it. Another user's session is therefore a 404, and its existence
  does not leak (§8 rule 3).
- No app page is specified for this; the result is visible through the API.

## In scope

- `ListSessionsUseCase`, `RevokeSessionUseCase`, and `sessions_controller.py`
  (§10).
- The list of the principal's unrevoked sessions with the device facts the ERD
  stores, and no token or hash (§9).
- Revocation with `revoked_by_user`, which also revokes the session's refresh
  tokens, answering 204.
- Another user's or an unknown session id: 404 (§7, §8 rule 3).

## Out of scope

- Revoking on password reset or change (T-10, T-12).
- Any app page.

## Acceptance

- The list holds only the principal's unrevoked sessions (§7, ERD).
- Revoking one of the principal's sessions returns 204 and sets `revoked_at`
  and `revocation_reason` `revoked_by_user`. That session's refresh token then
  fails with `session_ended` (§5, §7).
- Another user's session id returns 404, the same as an unknown id, and
  changes nothing (§7, §8 rule 3).
- No response holds a refresh token, a hash, or an access token (§9).

## Evidence required

- Ownership: one user's attempt on another user's session returns 404.
- The effect of revocation on that session's refresh.

## Implementation freedom

- The fields of each list item, and whether the requesting session is marked.
- Whether expired but unrevoked sessions appear in the list.
- Revoking the requesting session itself; §7 promises no failure for it.
