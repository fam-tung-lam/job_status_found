# Universal Behavior Contract

What a test must prove, whatever the language or runner. The package's
[precedence and exception policy](../SKILL.md#who-decides) governs these rules,
including Given-When-Then; this reference adds no separate hierarchy.

## Every test must

- check behavior through a public interface, not private methods, internal
  calls, or incidental structure;
- use Given-When-Then, through the tool's native API where one exists and
  otherwise through explicit `Given`, `When`, and `Then` comments;
- read as a behavior specification in the repository's domain words;
- take its expected values from a specification, a worked example, or a known
  literal, never from the production algorithm;
- cover one coherent behavior, using several assertions only when together they
  describe that one outcome;
- prefer real collaborators inside the chosen seam, replacing only a justified
  boundary;
- stay deterministic and isolated by controlling time, randomness, external
  services, and mutable global state at their boundaries; and
- clean up every resource it creates.

## Name a test after the behavior

A test name says what the caller observes, not which internal mechanism runs.
`empty queue returns none` survives a refactor; `calls _drain once` does not.

## Choose a level

Use a higher level only for a risk the lower one cannot establish. Never repeat
the same assertion across levels. Never let a coverage percentage stand in for
behavior-based design.

## Work test-first only when asked

Use Red-Green-Refactor only when the user explicitly asks for test-first work,
TDD, or Red-Green-Refactor by name. A request for tests, or for integration
tests, does not select it.

Work one observable behavior at a time:

1. Write the smallest test that specifies the next behavior.
2. Run it and confirm it fails for the expected missing behavior.
3. Write only enough production code to make it pass.
4. Rerun the focused test and confirm it passes.
5. Refactor only the code this behavior touched, then rerun the focused test.

Done when the behavior passes, the refactor keeps it passing, and every check
the stack specialization requires has run or is named as unavailable.

## Finish

Finish when every planned test states one observable risk and satisfies this
contract, before any stack-specific mechanic is chosen.
