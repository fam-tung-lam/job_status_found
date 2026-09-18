# Dart Futures, Streams, and Isolates

How Dart futures, streams, and isolates satisfy an owned asynchronous lifetime.

Dart runs one isolate's code on one thread. Nothing else in that isolate runs
while your function holds the turn, so any wait that is not an `await` stops the
whole isolate.

## Pick the type by how many values arrive

| Delivers           | Type           |
| ------------------ | -------------- |
| One value, later   | `Future<T>`    |
| Many values, later | `Stream<T>`    |
| Nothing, but ends  | `Future<void>` |

An `async` function always returns a `Future`. Declare that return type;
`avoid_void_async` reports an `async` function typed `void`, because a caller
then has nothing to await and no way to see it fail.

## Every `Future` gets an owner

Await the future, return it to its caller, or hand it to a supervisor that
observes errors and owns completion and shutdown. `unawaited` from `dart:async`
only marks intentional omission of `await`; it does not handle errors or supply
an owner. Use it only after that supervision exists, and name the handoff where
it is not obvious. Enable `unawaited_futures` to detect accidental omissions.

Attach failure handling before a future can fail. An unhandled asynchronous
error reaches the zone's error handler; a comment saying nobody waits does not
make that a recovery path.

Await independent work together:

```dart
final results = await Future.wait([fetchOrders(), fetchCustomer()]);
```

`Future.wait` joins the supplied futures. By default it waits for all to settle
and surfaces the first error, discarding later errors. Handle each future's
failure separately when the contract needs every outcome.

Bound external waits with `.timeout(...)`, and give `onTimeout` a value or let
it throw `TimeoutException`. This ends the wait, not the source operation. An
arbitrary `Future` has no cancellation method. Use the underlying API's
cancellation when available; otherwise keep the continuing work supervised
through bounded completion or handoff to a longer-lived owner.

Prefer `return future;` to `return await future;` inside an `async` function
when no surrounding `try` needs the result; `unnecessary_await_in_return`
reports the difference.

## Whoever listens, cancels

A `StreamSubscription` lives until someone cancels it. Store it in the object
that created it and cancel it in that object's teardown:

```dart
class Watcher {
  StreamSubscription<Order>? _subscription;

  void start(Stream<Order> orders) {
    _subscription = orders.listen(_handle);
  }

  Future<void> dispose() async {
    await _subscription?.cancel();
  }
}
```

Enable `cancel_subscriptions` and `close_sinks`: they catch the field that is
never cancelled and the `StreamController` that is never closed. A leaked
subscription keeps its source alive and keeps handling events after the owner is
gone.

A plain `StreamController` accepts one listener and throws on the second. Use
`StreamController.broadcast()` only when several listeners are really expected;
a broadcast stream drops events emitted while nobody listens. Prefer `async*`
and `yield` to driving a controller by hand when the source is a loop you own.

## Never block the isolate

Use the asynchronous form of every I/O call. `avoid_slow_async_io` flags the
async file and directory calls that are slower than their synchronous
counterparts, which is the one place the synchronous form is right.

Move CPU-bound work off the isolate with `Isolate.run`:

```dart
final total = await Isolate.run(() => sumEveryLine(rawCsv));
```

Anything that keeps the turn, such as a long loop, a large parse, or a
synchronous socket read, freezes every other callback in that isolate.

## Finish

Finish when each future is awaited, returned, or supervised, and `unawaited`
never substitutes for failure handling. External waits are bounded without
claiming the source work stopped, subscriptions and controllers are cancelled or
closed by their owner, and no synchronous call holds the turn for long.
