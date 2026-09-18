# Controlling Code Complexity

Keep code no more complex than the confirmed behavior and its safeguards
require. Shorter is better only when it keeps the right responsibility and clear
ownership.

## Prefer the first sufficient source

| Order | Prefer                                  | Sufficient when                                                      |
| ----- | --------------------------------------- | -------------------------------------------------------------------- |
| 1     | No implementation                       | The confirmed contract does not need the proposed behavior           |
| 2     | Delete or reuse repository code         | Existing owned behavior already satisfies the same contract          |
| 3     | Standard library                        | The supported runtime supplies the needed semantics                  |
| 4     | Native platform capability              | Every declared target supplies the behavior or an accounted fallback |
| 5     | An already-installed dependency         | Its existing contract and lifecycle cover the need without a new one |
| 6     | Minimum new code at the owning boundary | Earlier sources fail and new logic satisfies the whole behavior      |

When two sources are equally small, prefer the one that handles the confirmed
edge cases and makes ownership easiest to trace. A new dependency is justified
only when its maintained contract removes more repository ownership than its
install, update, security, licensing, and removal costs add.

## Keep complexity with its owner

- Put new behavior at the boundary already responsible for it.
- Fix a shared cause once when every affected caller already reaches that owner.
- Keep one coherent responsibility under one owner. Use
  [structure.md](structure.md) for file boundaries; a separate source file does
  not require another abstraction.
- Defer speculative behavior until a confirmed contract requires it.
- Prefer direct, established code over clever compression or indirection.
- Add an abstraction for a verified responsibility or contract boundary, or
  demonstrated variation. A boundary can be necessary with one implementation;
  similar syntax or a test double alone does not establish the need.
- Use [evolution.md](evolution.md) when deciding whether repeated implementation
  has revealed a stable pattern to extract.

A confirmed contract is the signal to add code. Adding system structure such as
a runtime, a store, or a second platform is an architecture decision outside
this skill.

## Require preservation evidence

A deletion, reuse, substitution, or abstraction change is acceptable only when
the matching evidence supports it.

| Decision                  | Required evidence                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| Delete code               | No reachable caller, registration, external contract, migration role, or required side effect     |
| Reuse repository behavior | The same inputs, outputs, failures, lifecycle, and ownership                                      |
| Use a library or platform | Supported runtimes and targets provide the needed semantics, edge cases, and fallback             |
| Remove a dependency       | All call sites, targets, license duties, supply-chain needs, and lifecycle duties are covered     |
| Add or remove abstraction | A verified responsibility or contract boundary, or demonstrated variation justifies the new shape |

Trace callers, shared implementations, boundaries, tests, configuration, and
generated owners before changing a responsibility. Account for reflection,
dependency injection, dynamic loading, code generation, external consumers, and
staged migrations when they can hide a use.

Keep required behavior and checks together with trust boundaries, data-loss
prevention, security, accessibility, compatibility, operability, and physical
calibration when they apply. Similarity, line count, a single-implementation
interface, or a delegating wrapper is a lead to inspect, not evidence that
removal is safe.
