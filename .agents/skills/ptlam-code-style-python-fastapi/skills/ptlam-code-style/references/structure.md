# Source Tree Structure

Where code lives, and how a folder listing reads to someone who arrived today.
The specialization owns the folder names a framework requires.

Where a system splits into components, runtimes, or stores is an architecture
decision outside this skill. This file owns where files live inside code one
team changes in one release.

## Name the top level after the domain

`billing/`, `scheduling/`, `ingest/`, not `controllers/`, `services/`, or
`models/`. The top-level listing should teach a newcomer what the system does,
not which framework built it. Layer names belong inside a capability, where the
framework needs them.

## Use the words the team uses

If people say "the reconciliation job" in standup, something in the tree is
called reconciliation. Every gap between the spoken word and the written one is
paid again in every conversation, review, and incident. When the domain renames
a concept, rename the code in a change of its own.

## Give each independently used API a file

Prefer a separate file for each class, component, or top-level operation callers
use independently, even when the file holds only one small declaration. An API
here includes a surface consumed by other files inside the same package; it need
not be published outside that package.

Name the file after that API so a folder listing reveals available behavior
without opening its implementations.

Keep a class's methods, tightly coupled contract types, and private helpers used
only by that API together. Several declarations may share a file when they form
one cohesive API; a shared topic alone does not make separate APIs one unit.

A thin export or index facade may publish several APIs while their
implementations remain in separate files.

Split an oversized implementation along named subresponsibilities a reader can
follow. Do not extract every method, add wrapper abstractions, or widen private
access just to meet a file, symbol, or line-count quota. Preserve
language-required declaration relationships and generator-owned layouts.

## Leave one obvious front door

Someone new should find the entry point and follow the main flow outward without
asking. Keep one entry point per runnable thing, thin enough to read in one
screen.

## Keep each listing readable at its own level

A folder is a table of contents, with each entry named after what it holds. Add
a folder when a real responsibility needs it, not to reduce the visible file
count. An empty layer tree invites files that do not belong. A folder holding
one file needs a domain or framework reason beyond satisfying a layout pattern.

## Match nesting to conceptual depth

Depth mirrors how the domain nests, not how careful the author felt. Seven
folders holding three files charge every reader seven decisions and return
nothing.

## Keep what changes together, together

Files that keep appearing in the same commit belong next to each other. Distance
in the tree should track conceptual distance, so a change lands in one place
instead of six.

## Make a capability deletable

Removing a feature should mean deleting its folder and the one place that
registers it. When removal turns into archaeology, the boundary is in the wrong
place; see [boundaries.md](boundaries.md).

## Prefer the structure people guess correctly

A tree someone can predict beats a better one they must learn. Uniformity is
what makes the tenth capability cheaper than the first.

## Keep the README about this repository

The README says what this is, how to run it, how to test it, where the main
pieces are, and who to ask. Everything else belongs in the document that owns
it.

## Finish

Finish when the top level names the domain, independently used APIs are
discoverable by file, each listing reads at its own level, and a capability can
be removed by deleting its folder and its registration.
