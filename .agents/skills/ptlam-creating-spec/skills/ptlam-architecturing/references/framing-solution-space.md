# Framing the Solution Space

This file covers the hidden dimensions behind common architecture debates, the
frame-first rule, and what each mark in a sketch must mean.

## Frame first, then position

A debate between two technology names has no shared map. Build the map before
choosing a path on it:

1. Name the dimensions the technology names stand for.
2. Draw the frame those dimensions span, usually two dimensions as a quadrant.
3. Name each region; a named region is remembered and reused.
4. Only then place the current state, each option, and the target.

The frame is not up for debate once named; the position is. Disagreement inside
one shared frame converges. Disagreement across two private frames never does.

## Dimensions behind common debates

Example: "monolith or microservices" hides two dimensions, design-time
modularity and runtime deployment granularity. Their quadrant holds four shapes,
not two, and names the modular monolith: modular design, one deployment. The
rows below are candidate dimensions, not answers; the position is still argued
on the frame.

| Debate                                            | Dimension one                    | Dimension two                      |
| ------------------------------------------------- | -------------------------------- | ---------------------------------- |
| Monolith or microservices                         | Design-time modularity           | Runtime deployment granularity     |
| Synchronous or event-driven                       | Coupling in time                 | Failure isolation between parts    |
| Relational or non-relational                      | Where consistency is enforced    | Fit to the measured access pattern |
| Kubernetes or plain VMs                           | Operational abstraction          | Operating skill on hand            |
| Specific or generic solution                      | Problems solved today            | Problems only imagined             |
| Build or buy                                      | Control over the capability      | Time to value                      |
| Micro-frontends or modular SPA                    | Design-time modularity           | Runtime deployment granularity     |
| Offline-first or thin client                      | Where the true state lives       | Tolerance for stale data           |
| Sync or async SDK API                             | Caller's blocking model          | Isolation from transport           |
| Single binary with plugins or in-tree subcommands | Who owns the extension point     | Distribution unit                  |
| Batch or streaming                                | Result latency                   | Cost per record and reprocessing   |
| Native or cross-platform                          | Platform fidelity                | Cost of a second implementation    |
| In-process library or sidecar                     | Upgrade independence             | Deployment coupling                |
| Paved path or self-service                        | Who operates the onboarding step | Consistency across consumers       |
| Bare metal or RTOS                                | Timing guarantees needed         | Code the team can trace            |

Add a dimension only when it changes which option wins. Two dimensions the
reader can hold at once beat five that need a legend.

## Give the sketch real meaning

A picture cannot be fuzzy: two boxes either share a line or they do not. Decide
what every mark means before drawing it, and keep it the same everywhere.

| Mark                    | Must mean one of                                    |
| ----------------------- | --------------------------------------------------- |
| Arrow                   | Data flow, control flow, or dependency; sync or not |
| Stacked boxes           | Several instances, not exactly the drawn count      |
| Nesting                 | Containment or ownership                            |
| Adjacency               | Shared boundary or shared runtime                   |
| Numbering               | Order of calls or of rollout                        |
| Size, shading, or shape | One declared quality, named in a legend             |

Draw back what you understood and invite "that is wrong". The correction is the
information the sketch exists to extract.

## Keep the map purpose-driven

Draw the scout's map, not the cartographer's: only the parts that bear on the
question, current as of this decision. A complete landscape is stale before it
is finished and serves no decision.

Finish when the frame has named dimensions and regions, every option and the
current state sit on it, and every mark has one declared meaning.
