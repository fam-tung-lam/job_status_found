# Changing Code Over Time

How today's change leaves the code for the twentieth one. The specialization
owns the migration, deprecation, and release tooling.

## Optimize the change you will make twenty times

Find the axis the work really moves along, such as a new payment method, a new
report, or a new locale, and make that one cheap. A structure tuned for a change
nobody repeats charges rent on every change somebody does.

## Use the third case to test a repeated pattern

For repeated implementation, waiting for a third case is a useful heuristic: it
tests whether the apparent common shape survives another real use. Two similar
blocks alone can hide different responsibilities. A wrong abstraction costs more
than duplication because its callers become coupled.

[complexity.md](complexity.md) owns whether an abstraction is justified. Case
count is not a prerequisite for a required boundary, and a third copy is not
permission to couple unrelated work.

## Spend deliberation on what you cannot undo

A stored data format, a published API, and an identifier scheme deserve a week.
A folder layout, an internal name, and a private helper deserve a decision and a
move on. Ask what reversal would cost, then spend accordingly. Deciding what you
cannot undo is an architecture judgment outside this skill; record the confirmed
decision as the last section below says.

## Migrate in parallel

Expand, migrate, contract: add the new shape beside the old one, move readers
and writers across, then remove the old one when nothing uses it. Every
in-between state ships. A big-bang switch is a rollback you cannot perform.

Keep the reverse of each step available and practiced: one command to release,
one to roll back.

## Keep the refactor out of the behavior change

A diff that both moves code and changes what it does cannot be reviewed or
reverted. Restructure in one commit, change behavior in the next, and say which
is which.

## Record what forced the decision

When a choice constrains the future, such as a format, a boundary, or a
dependency, write down what you chose, what you rejected, and what forced it.
Whether it deserves an architecture decision record is that record's own
qualification gate, outside this skill. The code survives; the reasoning
evaporates in about six months.

## Finish

Finish when the frequent change is the cheap one, every new abstraction meets
the complexity rule, each migration ships in stages, and any constraining
decision is written down with its cause.
