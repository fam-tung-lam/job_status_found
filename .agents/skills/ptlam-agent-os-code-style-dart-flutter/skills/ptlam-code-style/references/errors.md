# Failure and Recovery

How code fails, what it says when it does, and what it does about someone else's
failure. The specialization owns the exception, result, or error-value
mechanics.

## Design the error as part of the interface

A caller can only handle what you hand them. Name each failure for what
happened, carry the identifier of the affected thing, and make the message say
what to do next. "Something went wrong" hands the problem back unchanged.

## Decide each dependency's failure mode now

For every dependency, decide what happens when it is slow, down, or wrong before
shipping the call. Unspecified means unpredictable, and production picks for you
at the worst moment.

## Fail fast at startup

Missing or invalid configuration stops the process at once, with a message
naming the setting. A process that starts anyway surfaces the same problem hours
into a batch job, far from its cause.

## Separate an expected outcome from a bug

"Card declined" is business flow. "Column missing" is a defect. Represent an
expected rejection as a named, typed, stable outcome the caller can distinguish
from a defect without parsing a message.

Use one consistent reporting channel at each boundary. The language and boundary
mechanics choose a return value, result type, or typed domain exception. A
thrown business rejection does not become a program defect merely because it
throws; translate it into the promised public outcome at the boundary.

## Never swallow a failure

Handle it, or add context and let it travel on. An empty catch is a decision to
be confused later, and it is nearly invisible in review. Record the failure
once, where it is handled; [logging.md](logging.md) owns the record.

## Bound every retry

Every remote call gets a timeout. Every retry gets exponential backoff with
jitter and a budget that stops it. Retry only what the other side made safe to
repeat, as [contracts.md](contracts.md) requires. Unbounded retries turn someone
else's hiccup into an outage you caused.

## Prefer a clean crash to a limping process

A predictable stop with a clean restart beats a process quietly writing corrupt
data for hours. When an invariant is gone, stop instead of guessing.

## Finish

Finish when actionable failures are named and typed, expected rejections are
distinct from defects, and each boundary uses its promised reporting channel.
Remote waits and retries are bounded, invalid configuration stops startup, and
no path discards a cause.
