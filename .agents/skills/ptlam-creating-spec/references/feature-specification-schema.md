# Feature specification schema

This file covers the feature-spec shape, status rules, and the readiness checks
for ticket planning. Read it before writing or revising a spec.

## File shape

Use every heading. Write `None` with a reason when a section does not apply.

```markdown
# Feature specification: <feature>

- Status: <draft | blocked | ready>
- Updated: <timestamp>
- Source scope: <PRD path and heading, or feature brief>
- Glossary: <path, or unavailable>

## At a glance

<One literal paragraph that lets the reader rebuild the feature's purpose and
observable result.>

## Visual overview

<At least one earned Mermaid diagram or scan-friendly table that replaces the
equivalent prose.>

## Feature contract

<Who can do what, under which preconditions, and what observable result
follows.>

## Scope boundaries

### Included

<Behavior this feature owns.>

### Excluded

<Neighboring behavior this feature deliberately leaves out.>

## Behavior

### <B-01: descriptive behavior>

- Given: <observable starting state>
- When: <actor or system action>
- Then: <observable result>
- Failure: <rejection, recovery, or None with reason>
- Evidence required: <what must be proven, without test mechanics>

## Permissions and policy

<Authorization, policy, privacy, and compliance constraints.>

## Data and lifecycle

<Owned data, invariants, state transitions, retention, and deletion behavior.>

## Interfaces and compatibility

<Inputs, outputs, contracts, compatibility, and deliberate implementation
freedom.>

## Failure and recovery

<Validation, error visibility, retry, repeat-safety, concurrency, and degraded
behavior.>

## Operations and rollout

<Signals, migration, rollout, rollback, and support constraints.>

## Architecture constraints

### <A-01: structure expensive to reverse>

- Accepted structure: <the confirmed judgment and the boundary it fixes>
- Trade-offs: <what the structure gives up and why that is acceptable now>
- Deferred: <concern left out and the signal that adds it, or None>
- Redesign trigger: <the measured number, curve, or named event>
- Source: <architecture judgment, ADR, or confirmed statement>

## Assumptions and risks

<Assumptions with evidence, plus risks and their consequences.>

## Blocking decisions

<Decision, owner, consequence, and return path to decision work, or None.>

## Traceability

<Map each behavior ID to its source heading and affected contract or constraint.>
```

Use stable behavior and structure IDs. Keep an existing ID when revising its
wording. Retire an invalid behavior explicitly instead of reusing its ID.

## Status rules

| Status    | Meaning                                                    |
| --------- | ---------------------------------------------------------- |
| `draft`   | The contract is being written and is not yet checked       |
| `blocked` | An outcome-changing decision is missing or contradictory   |
| `ready`   | Every readiness check passes and ticket planning may begin |

Move from `draft` straight to `blocked` or `ready` after checking. A revision of
a ready spec returns to `draft` until the affected sections pass again. An
architecture recommendation the user has not confirmed is a blocking decision:
record it under Blocking decisions and set status `blocked`.

## Readiness checks

| Check        | The spec must                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------- |
| Source       | Name one confirmed scope source and cite a source heading for every behavior                   |
| Explanation  | Make unfamiliar content understandable without changing source facts                           |
| Visual       | Include one earned visual that replaces equivalent prose                                       |
| Boundary     | Separate included behavior, exclusions, and deliberate implementation freedom                  |
| Vocabulary   | Use glossary terms when available and hold no material term conflict                           |
| Behavior     | State observable success, validation, failure, and recovery behavior                           |
| Data         | Cover ownership, lifecycle, privacy, retention, and deletion                                   |
| Contracts    | State interface and compatibility promises without accidental design choices                   |
| Operations   | Cover signals, migration, rollout, rollback, and support impact                                |
| Architecture | Record each expensive-to-reverse structure with its trade-offs, deferred concerns, and trigger |
| Proof        | Name the evidence each behavior needs without prescribing test mechanics                       |
| Decisions    | Carry no unresolved outcome-changing decision                                                  |
| Traceability | Map each behavior ID back to its source and affected contract                                  |

Finish with status `blocked` when any check fails for missing evidence or a
missing decision. Finish with status `ready` only when all checks pass.
