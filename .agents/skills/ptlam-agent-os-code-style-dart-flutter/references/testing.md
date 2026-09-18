# Dart and Flutter Testing

The `package:test` runner, expression, and matcher mechanics, then the Flutter
mechanics for each test level, test double, BLoC test, and widget test, then the
monorepo's test-level order. This file owns how a test is spelled and run, not
what it must prove.

Add the runner as a development dependency with `dart pub add dev:test`.

## The runner finds `_test.dart` and nothing else

Put tests under `test/` in files whose names end `_test.dart`. A helper named
`test/helper.dart` never runs, which makes it a safe place for shared setup.

```bash
dart test                              # every suite
dart test test/orders_test.dart        # one file
dart test -n 'rejects an empty id'     # by name, as a regular expression
dart test -N 'rejects'                 # by plain-text name
dart test -t slow                      # by tag
dart test --coverage=coverage          # collect coverage into a folder
```

Put settings every run should share in `dart_test.yaml` beside `pubspec.yaml`,
such as `timeout`, `concurrency`, and tag definitions, so a developer and CI
behave the same without repeating flags.

## Structure with `group` and `test`

Nest `group` to name the declaration under test, and let each `test` name the
observable outcome. Setup runs per test, not per file:

```dart
void main() {
  late OrdersRepository repository;

  setUp(() {
    repository = OrdersRepository(FakeOrdersApi());
  });

  group('place', () {
    test('returns a confirmation for an accepted order', () async {
      expect(await repository.place(order), isA<Confirmation>());
    });
  });
}
```

`setUp` and `tearDown` run around every test in their group. Prefer
`addTearDown(subject.dispose)` inside the test that created the resource: the
cleanup sits beside the acquisition and cannot outlive it.

## Match the outcome, not the mechanism

| Outcome                       | Matcher                                                    |
| ----------------------------- | ---------------------------------------------------------- |
| A value                       | `expect(actual, equals(expected))`                         |
| A type                        | `expect(actual, isA<Confirmation>())`                      |
| A field of a thrown error     | `isA<ArgumentError>().having((e) => e.name, 'name', 'id')` |
| A specific throw              | `expect(() => f(), throwsArgumentError)`                   |
| No throw                      | `expect(() => f(), returnsNormally)`                       |
| A future's value              | `await expectLater(future, completion(equals(1)))`         |
| A stream's values, then close | `expect(stream, emitsInOrder(<Object>[1, 2, emitsDone]))`  |

Wrap the call in a closure for any `throws…` matcher; `expect(f(), …)` throws
before the matcher runs.

## Get the async right

Make the callback `async` and `await` the thing under test, or return its
future. A `test` body that starts work without awaiting it passes before the
work finishes. Use `expectLater`, not `expect`, whenever the matcher itself
completes later, and await the result.

The default timeout is 30 seconds per test. Change it on purpose with
`@Timeout(Duration(seconds: 5))` above the file's `library;` directive, a
`timeout:` argument on a `group` or `test`, or `--timeout` for one run. A test
that needs longer usually needs a controlled clock instead.

Mark a known-unfinished case `skip: 'reason'` rather than commenting it out, so
the runner reports it.

## Flutter test tools

Use the Flutter SDK's `flutter_test`,
[`bloc_test`](https://pub.dev/packages/bloc_test) for BLoC behavior, and
[`mocktail`](https://pub.dev/packages/mocktail) when the chosen double is a
mock.

`flutter_test` layers `testWidgets`, `WidgetTester`, and the Flutter finders and
matchers on top of the same `group`, `test`, `expect`, and matcher API that
`package:test` defines, and re-exports `Timeout`, `Skip`, `Tags`, and
`addTearDown`. Only the Flutter additions below belong here.

## Supported local levels

| Level             | Flutter mechanic                                                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local unit        | `fvm flutter test` without a widget tree                                                                                                                                  |
| Local integration | `fvm flutter test` with real collaborators inside the chosen boundary and doubles only outside it; pump a widget tree only when UI collaboration is part of that boundary |
| UI golden         | `fvm flutter test` with a stable surface, deterministic fonts, locale, size, theme, and an approved image baseline                                                        |
| End-to-end        | `fvm flutter test integration_test` on the smallest real target that exposes the chosen journey risk                                                                      |

The chosen level decides the command. A folder name does not, and a local
integration test need not pump a widget tree.

## BLoC tests

Use `blocTest` for event-driven state. Assert the emitted state sequence, not
internal fields.

- `build` constructs the BLoC with its collaborators.
- `seed` supplies the starting state without replaying setup events.
- `act` sends the event or calls the operation under test.
- `expect` lists the states after the seed, in order.
- `verify` checks an outgoing interaction only when the behavior contract makes
  it observable.

Seed the state the behavior needs. Replaying several events just to reach the
starting condition gives the test unrelated failure paths.

## Mocktail mocks

Declare a mock by hand; mocktail needs no generated file:

```dart
import 'package:mocktail/mocktail.dart';

class MockOrdersRepository extends Mock implements OrdersRepository {}
```

Keep a mock one test uses in that test file, and a mock several tests share in
`test_doubles/`. Before matching a custom type with `any()`, register a fallback
value once, for example in `setUpAll`, with `registerFallbackValue`.

An unstubbed mocktail method returns `null`, which fails at runtime for a
non-nullable return type. Stub every value the test uses, and stub async methods
with `thenAnswer`:

```dart
when(() => repository.place(any())).thenAnswer((_) async => confirmation);
verify(() => repository.place(order)).called(1);
```

## Widget tests

Pump through one shared helper that installs the theme, localization provider,
and required `BlocProvider`s. Prefer `pump()` with an explicit duration over
`pumpAndSettle()`.

When `pumpAndSettle` times out, look for a looping animation, an always-visible
progress indicator, or a stream that keeps emitting. Pump a fixed duration or
drive the state to a settled value. When a `blocTest` expectation never arrives,
check whether the emitting future was awaited and whether a `bloc_concurrency`
transformer dropped the event.

Find widgets through user-visible semantics or an agreed key, not widget type or
tree position.

## Monorepo: prove at the highest level first

These rules apply only in the monorepo described in
[SKILL.md](../SKILL.md#choose-the-layout). The foundation adds a higher level
only for a risk a lower level cannot establish. This project replaces that
order: a passing journey through the composed app tells the agent the whole path
works, and a unit suite alone cannot. Choose levels in this order and stop when
the remaining risk is covered:

| Order | Level             | Mechanic                                                                                                                                                          | Lives in                                            |
| ----- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1     | End-to-end        | `fvm flutter test integration_test` through `main()` on macOS or web; one journey per user-visible outcome you changed                                            | `apps/ptlam_agent_os/integration_test/` only        |
| 2     | Local integration | `fvm flutter test` pumping the feature's page with its real BLoC, use cases, and adapters; replace only the API client or platform plugin at the package boundary | `<package>/test/integration/`, mirroring `lib/src/` |
| 3     | UI golden         | `fvm flutter test` with deterministic fonts, locale, size, theme, and an approved image baseline                                                                  | `<package>/test/golden/`                            |
| 4     | Local unit        | `fvm flutter test` without a widget tree, for input combinations, failure mapping, and domain rules the levels above cannot reach economically                    | `<package>/test/unit/`, mirroring `lib/src/`        |

Every change to user-visible behavior adds or extends one end-to-end journey and
one local integration test in the owning feature. Add unit tests for the edge
cases those two leave uncovered; do not repeat their assertions. When the
end-to-end target cannot run on your machine (no macOS runner, no ChromeDriver),
run the local integration level and name the skipped journey in the handoff.

## Monorepo: where tests run

Every test runs inside the package that owns the code under test. Run one
package with `fvm flutter test` from its directory; run every package with
`melos run test` from `src/app`; run end-to-end journeys with the
`test:e2e:macos` and `test:e2e:web` Melos scripts. The selected level determines
the command; a directory name does not.

Doubles shared across levels go in `<package>/test/test_doubles/`; a double one
level uses stays in that level's `test_doubles/`. Find widgets through an agreed
`ValueKey`, as the existing smoke test does, and follow its Given, When, Then
comment shape.

Finish when every new test file ends `_test.dart`, each test awaits everything
it starts, every resource it creates is released by `addTearDown` or `tearDown`,
every mock stubs the values the test uses, and the affected suites pass under
`dart test` or `fvm flutter test`.
