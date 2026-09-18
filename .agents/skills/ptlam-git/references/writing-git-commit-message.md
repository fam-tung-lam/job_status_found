# Writing a Git Commit Message

Write one commit message whose subject, optional body, and issue references
match the inspected change and the repository's policy.

## 1. Resolve the message policy

Apply preferences in this order:

1. The user's explicit message instructions.
2. The applicable `AGENTS.md` or similar repository instructions.
3. A repository policy file those instructions name.
4. The portable defaults below.

Report a conflict instead of quietly applying a lower preference. Treat
neighboring commit history as evidence, not as policy, unless the user or the
repository instructions make it policy.

Done when every message choice has one controlling source.

## 2. Draft the subject

Use Conventional Commits by default: `<type>(<scope>): <description>`. Drop the
scope when it adds nothing.

- Prefer `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`,
  and `ci` as types.
- Name the outcome, capability, fixed behavior, or reason for the refactor.
- Start the description with a lowercase imperative verb.
- No final period; aim for 50 characters and never exceed 72.

Done when the subject describes the whole inspected change on its own.

## 3. Add the body and issue references

Add a short body when the subject cannot carry the needed reason or impact.
Always add one for a breaking change, a security fix, a migration, or a revert.
Explain why the change exists, not how it was made.

Add `Fixes #<issue>` or `Closes #<issue>` only when the change resolves a
verified issue. Use `Relates #<issue>` when it contributes without closing. Use
the full URL for an issue in another repository.

Done when every body paragraph and reference carries information the subject
cannot.

## 4. Check and return the message

Read the subject alone. Confirm it matches the change, uses the right type and
scope, starts with a lowercase imperative verb, meets the length rules, and
agrees with the body.

Verify every issue reference against the request or repository evidence. Return
the exact subject and body with real line breaks, and say what was not fully
verified.
