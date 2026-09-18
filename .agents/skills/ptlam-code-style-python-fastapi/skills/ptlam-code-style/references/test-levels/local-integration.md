# Local Integration Testing

Use a local integration test when the risk lies in collaboration between real
components, adapters, processes, storage, or framework services inside a chosen
test-harness boundary.

"Local" names the harness boundary, not where the test command runs. Classify by
the exercised boundary, not by the framework's suite name. A suite called
`integration` is end-to-end under this skill when it starts the composed
application and drives a user journey through its real entry point.

## Rules

- Place the test where [test-placement.md](../test-placement.md) resolves.
- Define the integration boundary and the behavior visible through its public
  entry point.
- Run the real collaborators whose compatibility is the subject.
- Replace only dependencies outside the chosen boundary, especially
  uncontrollable remote services.
- Exercise locally controlled filesystem, database, subprocess, package, or
  platform adapters for real when their integration is the risk.
- Use isolated data and resources. Create, identify, and clean them up within
  the test lifecycle.
- Assert behavior through the public boundary, not by querying internals.
- Keep the suite smaller than the local unit suite and cover collaboration
  failures rather than repeating unit cases.
- Prefer deterministic readiness signals over sleeps.

## Test doubles

Keep integration doubles apart from unit doubles even when they represent a
similar external dependency. A unit double isolates the unit; an integration
double excludes something outside the boundary. Share one definition above both
level folders only when the same double is really reused at both levels.

## Exit criteria

- The real collaborators under test were exercised.
- A failure identifies a broken integration contract, not an unrelated external
  outage.
- The same risk is not already fully shown at a cheaper level.
