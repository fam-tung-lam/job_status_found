# Logging

The Flutter mechanics for emitting, routing, and sanitizing log records.

## `AppLogger` is the only entry point

`AppLogger` lives in `lib/packages/<project_name>_logger/` and wraps
[`logging`](https://pub.dev/packages/logging). Application code depends on
`AppLogger` and never imports `package:logging` directly.

Never use `print` or `debugPrint` in application code. They ignore the level
policy, ship to release builds, and cannot be captured by a crash reporter.

Give each logger a name under the project root, derived from where it logs:

```dart
final _log = AppLogger.of('orders.repository');
```

## Configure once, in `main`

Set `Logger.root.level` and the record handler once during startup, before
`runApp`. Nothing else changes the level at runtime except a deliberate
developer setting. Log verbosely in debug and sparingly in release, chosen by
build mode.

## Route framework errors into the same logger

Wire both handlers during startup so a widget error and an unhandled async error
land with everything else:

- `FlutterError.onError` for errors raised inside the framework.
- `PlatformDispatcher.instance.onError` for uncaught async errors.

Without them, a build failure prints to the console and is invisible in the
release build's reporting.

## Where to log

| Layer                                                                  | Logs                                                         |
| ---------------------------------------------------------------------- | ------------------------------------------------------------ |
| The boundary that converts an external cause into a domain failure     | The sanitized operation and cause, once, at debug or warning |
| Other clients, data sources, and repositories on the same failure path | Nothing; attach context without a duplicate record           |
| Use case, BLoC                                                         | Nothing routine; a state transition is not an event          |
| Widget                                                                 | Nothing                                                      |

## Never log a request body

Dio's logging interceptor prints headers and bodies by default, including the
`Authorization` header, tokens, and whatever the user typed. Log the method, the
path, the status, and the duration. Nothing else leaves the client.
