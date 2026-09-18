# Asynchronous Work Lifecycle

Who owns asynchronous work from creation through completion or shutdown. The
specialization supplies futures, tasks, subscriptions, and cancellation APIs.

## Keep the work inside a lifetime

Prefer work awaited by the scope that starts it. Work that must outlive that
scope needs an explicit handoff to a longer-lived owner before the scope exits.
A discarded handle or a comment about background work is not a handoff.

| Obligation  | Owner must establish                                                        |
| ----------- | --------------------------------------------------------------------------- |
| Ownership   | Which scope or component keeps the operation and its resources alive        |
| Completion  | Who consumes the result, or deliberately discards a successful value        |
| Failure     | Who observes and handles or propagates the failure                          |
| Waiting     | What bounds external waits and shutdown, including retries                  |
| Termination | How cancellation reaches supported work, or how other work completes safely |
| Cleanup     | When subscriptions, handles, and other resources are released               |

Long-lived work can run for the owner's lifetime. Its shutdown still needs a
bounded plan. When cancellation is unavailable, choose bounded completion or
handoff to another explicit owner; retain failure observation and cleanup until
the actual work ends.

## Separate a wait ending from the work ending

A timeout can stop the caller's wait while the underlying operation continues.
Cancellation can be cooperative and require the operation to observe it.
Determine what the actual API guarantees before releasing resources or reporting
that work has stopped. Suppress late results only when the contract allows it;
that does not erase outstanding failures or cleanup duties.

## Finish

Finish when each asynchronous operation has a named lifetime, every result and
failure has a destination, waits and shutdown are bounded, and resources remain
owned until completion or confirmed termination.
