# Test Doubles

Use a test double only at a justified boundary. Prefer the real collaborator
inside the chosen seam when it is fast, deterministic, and safe. When a double
is needed, use the repository's approved mocking dependency and give every
reusable double one nearest common owner.

## Choose the role

- **Dummy:** satisfies a required parameter but is never used.
- **Stub:** supplies predetermined input.
- **Fake:** a simplified working implementation of a boundary.
- **Spy:** records outgoing interactions for later assertions.
- **Mock:** carries predetermined interaction expectations and verifies them.

Name and discuss a double by the role it performs even when one API creates
every role through a type named `Mock`. Use the simplest role that expresses the
needed behavior. Verify an interaction only when it is part of the observable
contract.

## Resolve the mocking tool

- Reuse the repository's approved mocking dependency.
- In a read-only review, report a missing or conflicting dependency without
  changing files.
- With no dependency, recommend one that fits the existing test runner and add
  it only within allowed dependency scope.
- When another mocking library already exists, do not quietly add a second.
  Recommend keeping, migrating, or deferring, with the trade-off.
- Take implementation mechanics from the installed tool's type declarations,
  command help, or accepted examples. If none confirms the mechanic, report the
  gap instead of inventing an API.

Done when one repository-compatible mechanism owns every new double in scope.

## Place a reusable double at the nearest common scope

Start from the layout [test-placement.md](test-placement.md) resolves. Placement
follows the consumers, not a fixed repository-wide folder:

| Consumers                      | Where the definition lives                                                         |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| One test                       | Inside that test                                                                   |
| Several cases in one file      | Inside or beside that file's suite                                                 |
| Several neighboring test files | The repository-named test-doubles folder in their nearest common test-owned folder |
| Several nested test folders    | Their nearest common parent                                                        |

In a separate test-root layout, a level-specific double stays inside its level.
A double already reused across levels belongs at the nearest common capability
scope:

```mermaid
treeView-beta
    <test-root>/
        <capability>/
            <test-doubles>/ ## Shared across levels
            <local-unit-level>/
                <test-doubles>/ ## Local unit only
            <local-integration-level>/
                <test-doubles>/ ## Local integration only
```

In a source-adjacent layout, keep the double beside the nearest common group of
test files:

```mermaid
treeView-beta
    <source-root>/
        <capability>/
            <test-doubles>/ ## Used by neighboring tests
            first_test.<ext>
            second_test.<ext>
```

Use the repository's spelling, such as `test-doubles` or `test_doubles`.

- Keep one reusable double or generation declaration per file unless the tool
  requires another layout.
- Do not create a suite-root double folder on speculation.
- Keep doubles for different levels apart unless the exact same definition is
  already reused across them.
- Let a fixture or hook build and clean up a reusable double while its
  definition stays at the nearest common scope.
- Keep one-off mocks, patches, and expectations in the test.
- When reuse grows, move the original definition instead of copying it. When
  reuse shrinks, move it closer to the remaining consumers.
- Remove the old definition and update every import after a move.

Done when each definition has the smallest owner that holds all real consumers
and no broader speculative copy remains.

## Avoid false confidence

- Do not replace internal collaborators just to assert call counts or order.
- Do not reproduce the production algorithm in conditional setup.
- Keep stubbing in the Given phase.
- Prefer fresh doubles per test over shared mutable state and broad resets.
- Fail or report when an unstubbed or default value affects the asserted
  outcome.

The double is valid only when breaking the boundary contract fails the test
while an internal refactor that keeps behavior does not.
