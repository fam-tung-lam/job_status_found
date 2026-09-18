---
name: ptlam-code-style
description:
  Hold source and test code to one language-neutral standard for complexity,
  source structure, boundaries, naming, readability, domain modeling,
  cross-boundary contracts, failure design, asynchronous lifetime,
  documentation, logging, evolution, and testing. Use when no stack
  specialization matches the project, and as the foundation every stack
  specialization composes. Use ptlam-modeling-domain instead for business terms
  and context boundaries, and ptlam-architecturing instead for a component,
  runtime, or data-store split, a published surface, state ownership, or a
  platform commitment.
---

# PTLam Code Style

Route every source and test concern through one language-neutral standard. This
foundation owns the shared rules and words. A stack specialization owns the
mechanics that satisfy them. When a specialization matches the project, use it;
it loads this skill for you.

Every entry point inherits the same source and test invariants: cohesive
responsibilities, small published surfaces, directed dependencies, explicit
state ownership, and observable behavior. Preserve confirmed system boundaries.

## Who decides

Use this policy for source code, tests, and every reference in this package. For
an open question, take the first source that owns it:

| Order | Source                                         | Owns                                                                     |
| ----- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| 1     | The user's current instructions                | Anything the user states for this task                                   |
| 2     | The applicable `AGENTS.md`                     | Project requirements and permitted exceptions                            |
| 3     | The feature specification and repository files | Confirmed behavior and constraints; established commands, config, layout |
| 4     | The active stack specialization                | Stack mechanics the repository leaves open                               |
| 5     | This skill                                     | The rules below and the fallbacks they point to                          |

An explicit user or project instruction may replace a named rule; record that
replacement in the handoff. Repository examples and tool defaults are evidence,
not permission to override a rule. A specialization supplies mechanics or
stricter rules; it cannot silently weaken a shared invariant. Report unresolved
conflicts instead of choosing quietly.

A justified readability exception may change a presentational convention, such
as formatting or wording. Record its reason where the surprise lives, as
[documentation.md](references/documentation.md) requires. This exception never
waives behavior, security, contract, test, or lifetime guarantees.
Given-When-Then and the other test rules still apply unless explicitly replaced
above.

## Pick a reference

Read the one reference for the concern in front of you. Each owns its rules,
examples, and caveats.

| Concern                                                                 | Reference                                                                                                                                                                                                                                               |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Placing a file, adding a folder, or shaping the source tree             | [structure.md](references/structure.md)                                                                                                                                                                                                                 |
| Deciding what a unit publishes, which way it depends, where I/O sits    | [boundaries.md](references/boundaries.md)                                                                                                                                                                                                               |
| Naming a file, type, function, variable, or boolean                     | [naming.md](references/naming.md)                                                                                                                                                                                                                       |
| Writing or reshaping the body of a function                             | [readability.md](references/readability.md)                                                                                                                                                                                                             |
| Writing a doc comment, or explaining why code is the way it is          | [documentation.md](references/documentation.md)                                                                                                                                                                                                         |
| Shaping a domain type, a stored record, or a set of states              | [data-modeling.md](references/data-modeling.md)                                                                                                                                                                                                         |
| Promising something across a process, team, or release boundary         | [contracts.md](references/contracts.md)                                                                                                                                                                                                                 |
| Designing a failure, a retry, or a startup check                        | [errors.md](references/errors.md)                                                                                                                                                                                                                       |
| Starting asynchronous work, handing it off, or ending its lifetime      | [async-lifecycle.md](references/async-lifecycle.md)                                                                                                                                                                                                     |
| Emitting a log record, naming a logger, or picking a level              | [logging.md](references/logging.md)                                                                                                                                                                                                                     |
| Choosing sufficient code, reuse, deletion, a dependency, an abstraction | [complexity.md](references/complexity.md)                                                                                                                                                                                                               |
| Abstracting a repeated pattern, migrating a shape, recording a decision | [evolution.md](references/evolution.md)                                                                                                                                                                                                                 |
| Deciding what a test must prove, or working test-first on request       | [behavior-contract.md](references/behavior-contract.md)                                                                                                                                                                                                 |
| Choosing one test level for a risk                                      | The behavior contract, then [local-unit.md](references/test-levels/local-unit.md), [local-integration.md](references/test-levels/local-integration.md), [ui-golden.md](references/test-levels/ui-golden.md), or [e2e.md](references/test-levels/e2e.md) |
| Placing a new test file, or moving a misplaced one                      | [test-placement.md](references/test-placement.md)                                                                                                                                                                                                       |
| Adding, naming, or placing a test double                                | [test-doubles.md](references/test-doubles.md)                                                                                                                                                                                                           |

Choosing a component, runtime, or store split, a published contract, state's
source of truth, or a platform commitment needs an architecture decision outside
this skill. Hand an uncovered choice back to the caller before implementing it;
local code organization does not reopen a confirmed decision. Business
vocabulary is domain-modeling work outside this skill.

## Do the work

1. Resolve the project, then read the user's instructions and every applicable
   `AGENTS.md` from the root down to the files in scope. Choose review or change
   mode from the authorized request.
2. Name the concern and read its one reference. For every test, read the
   behavior contract before choosing a level, placement, or double.
3. Pick the active stack specialization. When none matches, say so instead of
   inventing a toolchain.
4. In change mode, apply the rules within scope. In review mode, interpret every
   implementation imperative as a conformance check and report defects.
5. Run the project's existing checks whose effects are known and permitted in
   that mode. Report exact commands, results, and missing evidence.

When build, test, or run is not one fast command, name that friction in the
handoff. A loop people avoid is a defect in the project.

A review does not edit source, add tests, format or fix files, generate code,
install or sync dependencies, run migrations, update snapshots, or rewrite
baselines. Build and test commands may create temporary output only where the
review permits it; inspect scripts and hooks first. Use check-mode counterparts
or report the unavailable check. Repairs require change authority.

## Finish

Finish a review with findings and verification limits. Finish a change when the
scoped files satisfy their rules and required checks pass. In either mode, every
open mechanic has a named owner, every permitted deviation carries its reason,
and the handoff never implies an unrun check passed.
