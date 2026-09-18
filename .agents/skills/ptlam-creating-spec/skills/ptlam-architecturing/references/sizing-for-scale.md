# Sizing for the Next Order of Magnitude

This file covers the demand unit and starting shape per system kind, what to
defer until a signal, the exceptions, day-zero concerns at an established base,
the complexity each kind cannot remove, and the triggers for the next redesign.

## Size to measured demand

Measure demand in the unit the system's kind counts. Design for about ten times
it where the kind scales, or for the fixed budget where it does not. The point
where a shape must change arrives later than intuition says.

| System kind          | Demand unit                         | Starting shape                                                             |
| -------------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| Server or full-stack | Requests or events per second       | One instance per stateful component; one database primary with one replica |
| Web frontend         | Concurrent sessions, bundle size    | One modular application with one build                                     |
| Mobile               | Installs, sessions, offline minutes | Thin client until measured offline sessions exist                          |
| SDK or library       | Consumers, host versions            | One transport, one published surface, versioned from the first release     |
| CLI                  | Installs, OS and shell matrix       | One binary; subcommands in one tree; no plugin interface                   |
| Data pipeline        | Records per window, backfill size   | Batch on one worker until the window is missed on the measured curve       |
| Embedded or device   | Flash, RAM, power, fleet size       | Fixed resource budget measured against the device, never scaled            |
| Desktop              | Installs, OS matrix, document size  | Local store is the truth; no sync service                                  |
| Internal platform    | Teams served, services onboarded    | One paved path for the first two teams                                     |

## Defer until a signal

| Concern                 | Add it when                                                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Caching                 | A measured hot path, or a projected one inside the planning horizon                                                        |
| Non-relational storage  | The primary cannot keep up and sharding is not an option                                                                   |
| Horizontal scaling      | Vertical capacity, which reaches hundreds of cores and terabytes of memory, is about 80 percent used on the measured curve |
| Container orchestration | Several services and the operating skill to run the platform both exist                                                    |
| Offline sync            | Measured sessions run without connectivity                                                                                 |
| Plugin interface        | A third external author needs to extend the tool                                                                           |
| Async API surface       | A host exists that cannot block                                                                                            |
| Streaming               | The batch window is missed on the measured curve                                                                           |
| Second platform         | Measured users exist on it                                                                                                 |
| Multi-tenancy           | A second tenant arrives with a conflicting need                                                                            |
| Cross-device sync       | A measured share of users open the same data on two devices                                                                |
| Self-service platform   | A third team waits on the platform team for the same onboarding step                                                       |

Exception: when a limit will be reached inside the planning horizon and the
money will not be available later, build for it now and record that reason in
the report.

## Day-zero concerns at an established base

When the system already serves a large base, a failure is public and rollback is
slow. Treat these as design inputs, not later additions. Authorization,
authentication, and data sensitivity are constraints at every size.

| System kind          | Day-zero design input                                                                  |
| -------------------- | -------------------------------------------------------------------------------------- |
| Server or full-stack | Query shape, data access patterns, gradual rollout behind feature flags                |
| Web frontend         | Staged rollout and cache invalidation                                                  |
| Mobile               | Kill switch and staged rollout; store review slows rollback                            |
| SDK or library       | Compatibility window and deprecation path                                              |
| CLI                  | Backward-compatible flags and exit codes                                               |
| Data pipeline        | Replay and backfill                                                                    |
| Embedded or device   | Field-update path and rollback image                                                   |
| Internal platform    | Migration path for already onboarded services                                          |
| Desktop              | Auto-update channel with rollback; local-store migration tested against prior versions |

## Keep the complexity that cannot be removed

Each kind carries complexity no design removes. Do not pretend it away; make it
easy to handle.

| System kind        | Built-in complexity                                           |
| ------------------ | ------------------------------------------------------------- |
| Distributed server | Retries, timeouts, repeat-safety, back pressure, retry storms |
| Mobile             | Connectivity loss, process death, background execution limits |
| SDK or library     | Consumer version skew, host runtime differences               |
| CLI                | Shells, exit codes, TTY versus pipe, signal handling          |
| Data pipeline      | Late and duplicate data, schema drift, backfill               |
| Embedded or device | Power, memory, no debugger in the field                       |
| Web frontend       | Browser matrix, cache invalidation, partial page failure      |
| Desktop            | OS matrix, local data migration across versions               |
| Internal platform  | Consumer version skew, migrating onboarded services           |

Remove complexity that is not built in: speculative abstractions, layers for
imagined variants, and structure chosen for status. Write the simplest structure
the team can trace end to end. A simple result is success.

## Plan the next redesign

Software is evolved, not built. Say in the report which measured number, curve,
or named event starts the next investment. Revisit that projection every quarter
to every year, because confidence decays with distance. When the demand curve is
visible and the current shape is used up, redesign from data, not from the
original plan. Migrations are part of the job, not a failure.

Finish when the recommendation names its demand unit and measured baseline, its
ten-times target or fixed budget, each deferred concern with its signal, and the
redesign trigger.
