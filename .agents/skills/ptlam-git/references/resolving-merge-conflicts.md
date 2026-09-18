# Resolving Merge Conflicts

Resolve every conflicted hunk in one authorized in-progress merge, rebase, or
cherry-pick, check the combined result, and finish without inventing behavior or
aborting.

## 1. Establish the operation and its goal

Run `git status --short --branch`, `git diff --name-only --diff-filter=U`, and
`git ls-files -u` in the conflicted worktree. Use the full `git status` when its
next-step guidance is unclear.

Read the request, the applicable repository instructions, and recent history.
Name the operation's goal, every unmerged path, and any unrelated change that
must stay untouched.

Done when the operation, goal, conflict set, and protected changes are explicit.

## 2. Recover both intents

For each conflict, inspect the working file and the index stages with
`git show :1:<path>`, `git show :2:<path>`, and `git show :3:<path>`. Use
`git log`, `git show`, and `git blame` as the history requires.

Read the stages by operation. In a merge, stage 2 is the current side and stage
3 is the incoming side. In a rebase, stage 2 is the branch being rebased onto
and stage 3 is the commit being replayed. In a cherry-pick, stage 2 is the
integration branch and stage 3 is the approved commit being applied. Never pick
a side from the words `ours` or `theirs` alone.

Follow linked pull requests, issues, or tickets when local history does not
explain an intent and the user allowed remote access. For a generated file, find
the authored source and the generator instead of resolving the output.

Done when each hunk has two named intents, evidence for each, and a judgment on
whether they are compatible.

## 3. Resolve every hunk

Keep both intents when they are compatible. When they are not, keep the
evidenced intent that matches the operation's goal and record which intent the
resolution drops.

Edit the authored source, remove every conflict marker, and regenerate derived
files through the repository's documented command. Take a whole side only when
the evidence shows the whole file should come from that side and the stage
mapping is verified.

Never add behavior neither side intended. Keep going until
`git diff --name-only --diff-filter=U` names no path and `git diff --check`
reports no marker or whitespace error.

Done when no unmerged path or conflict marker remains.

## 4. Prove the combined result

Find the required checks in repository instructions, CI configuration, and
project manifests. Run the type check first, then tests, then formatting and
lint. Run every pre-merge gate the repository requires.

Fix only failures the resolution caused. Rerun each failed check after the fix
and read formatting changes before staging them.

Done when the required checks pass, or every unavailable check and its impact
are named.

## 5. Finish the operation

Stage the resolved paths explicitly and confirm `git ls-files -u` is empty. For
a merge, create the merge commit with the intended message. For a rebase, run
`git rebase --continue`; for a cherry-pick, run `git cherry-pick --continue`.
Repeat this workflow for each later conflict until all approved commits finish.

Never abort or discard the operation without explicit permission. Do not skip a
replayed commit unless the repository proves its whole intent is present.

Verify with `git status --short --branch` and the relevant history. Report the
operation completed, the intent decisions and trade-offs, the checks run, and
any remaining unrelated changes.
