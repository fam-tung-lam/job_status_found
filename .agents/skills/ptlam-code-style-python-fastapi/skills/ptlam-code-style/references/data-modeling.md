# Data and Domain Modeling

How the domain's values are shaped before storage or transport touches them. The
specialization owns the type system, the data-model library, and the
serialization mechanics.

This file owns domain types in code. Shared business language, context
boundaries, and business process maps are domain-modeling work outside this
skill; use its terms as evidence, then express them with the code types owned
here.

## Model the domain, then persist it

Shape the core types around what the business means, then map them to storage.
When the table layout shapes the type, every business rule ends up written in
the database's vocabulary.

## Let types carry the contract

Types are the cheapest documentation. `UserId` and `OrderId` are not both
"string", and money is not a float. Encode identity, unit, and currency so the
checker catches what review will not.

## Prefer values that do not change

A value that cannot change can be passed, cached, and reasoned about without
tracing who touched it last. Reserve mutability for state that really evolves,
and give that state one owner (see [boundaries.md](boundaries.md)).

## Keep one source of truth

Store a fact once and derive the rest. Every copy is a future inconsistency with
a date on it, because the second writer never knows about the first.

## Make time explicit

Tell an instant from a calendar date, and event time from processing time. Carry
the zone. A bare "date" is a bug waiting for a daylight-saving change.

## Represent absence honestly

No `-1`, no empty string, no `1970-01-01` standing in for "we do not know". A
sentinel escapes into reports and dashboards years later, and by then nobody
remembers it was a placeholder.

## Name the legal states

Four booleans imply sixteen states, of which perhaps three are legal. Name those
three and let one type carry them. Make an illegal state impossible to build
before defending against it with validation.

## Split persistence from the domain when the shapes disagree

Keep one shape while the domain and the stored record still agree. Split them
the moment they stop agreeing: a premature second model is ceremony, a late one
is a rewrite. A specialization may require the split earlier at a boundary whose
shape someone else owns, such as a vendor's wire format.

## Finish

Finish when every value states its unit and identity in its type, absence is
representable without a sentinel, the legal states are named, and each fact is
stored in exactly one place.
