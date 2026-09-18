---
name: ptlam-agent-os-code-style-dart-flutter
description:
  Write, review, and fix Dart and Flutter code against conventions for the FVM
  toolchain, analyzer and formatter, naming, libraries, types, failures, async
  work, dartdoc, the four-layer feature structure, BLoC and Cubit state,
  widgets, routes, models, networking, storage, hand-written localization,
  logging, and tests, with no code generation. In the PTLam Agent OS src/app
  monorepo, also apply its app, feature, and package kinds,
  ptlam_agent_os_lints, Melos commands, cross-package composition and routing,
  and test-level order. Use when adding or changing Dart or Flutter code,
  choosing between setState, Cubit, and Bloc, placing a file or feature, wiring
  get_it or go_router, adding translations, or fixing an analyze, format, test,
  or melos failure. Do not use for another stack.
---

# PTLam Agent OS Code Style Dart Flutter

Rules for Dart and Flutter code: SDK and package resolution, analyzer and
formatter settings, naming, library layout, data types, failures, async work,
and dartdoc; then the four-layer feature structure, presentation state, widgets,
routes, external boundaries, localization, and tests; then the PTLam Agent OS
`src/app` monorepo's package kinds, Melos commands, cross-package composition,
and test-level order. This skill owns Dart, Flutter, and monorepo mechanics; the
foundation owns everything else.

## Required skills

### `ptlam-code-style`

**Reason:** Provides the language-neutral conventions and testing doctrine the Dart, Flutter, and monorepo mechanics satisfy. This skill does not repeat them.

**Instructions:** Loading the foundation is required, not optional background.

1. Read `skills/ptlam-code-style/SKILL.md` in full before any review
   or change.
2. Before each task, read every foundation reference the table below
   names for it. Paths are relative to this skill.
3. Record each foundation reference you read for the Finish list.

| Task                                                     | Read first under `skills/ptlam-code-style/references/`                         |
| -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Any review or change                                     | `complexity.md`                                                                |
| Adding or moving a file, module, package, or feature     | `structure.md`, `boundaries.md`, `naming.md`                                   |
| Writing or changing a function body                      | `readability.md`, `naming.md`                                                  |
| Adding or changing a public name or doc comment          | `documentation.md`, `naming.md`                                                |
| Designing a DTO, entity, value object, or state set      | `data-modeling.md`                                                             |
| Changing a route, API shape, or other published contract | `contracts.md`, `evolution.md`                                                 |
| Raising, translating, retrying, or mapping a failure     | `errors.md`                                                                    |
| Starting async work, a stream, or a BLoC lifetime        | `async-lifecycle.md`                                                           |
| Emitting or configuring logs                             | `logging.md`                                                                   |
| Adding a dependency, abstraction, or shared helper       | `complexity.md`, `evolution.md`                                                |
| Writing or changing a test                               | `behavior-contract.md`, `test-levels/`, `test-placement.md`, `test-doubles.md` |

Rules agents most often miss:

- Every test uses Given-When-Then; in `flutter_test` and
  `package:test`, write explicit `// Given:`, `// When:`, and
  `// Then:` comments.
- A test checks behavior through a public interface, never private
  methods or internal call counts.
- Expected values come from a specification, worked example, or
  literal, never from the production algorithm.
- A test name states what the caller observes, not the mechanism.
- A higher test level covers only a risk the lower one cannot, and no
  assertion repeats across levels; in the monorepo, this skill's
  highest-level-first order replaces that rule.
- Red-Green-Refactor applies only when the user asks for test-first
  work by name.
- Stubbing stays in the Given phase, with fresh doubles per test.
- Comments explain why, and a deliberate deviation carries its reason
  where it lives.
- A failure is never swallowed, and every retry is bounded.
- A log record is written once per event and never holds a secret or
  personal data.
- An unresolved conflict is reported, never settled quietly.

This skill may be stricter than the foundation, never less strict,
except where a monorepo mechanic replaces a foundation fallback, such
as the test-level order. The foundation's "Who decides" table
resolves any conflict.

Read [ptlam-code-style](skills/ptlam-code-style/SKILL.md).

## Choose the layout

The monorepo rules apply only when `src/app/pubspec.yaml` names
`ptlam_agent_os_workspace`. Those rules are Melos, the `ptlam_agent_os_lints`
rule set, the app, feature, and package kinds, and `docs/adrs/`. In every other
project, use the single-package Flutter layout in
[file-organization.md](references/file-organization.md) and skip each section or
reference marked for the monorepo.

In the monorepo, the package kinds and their dependency direction are:

| Kind    | Lives in                          | May depend on         | Owns                                                                   |
| ------- | --------------------------------- | --------------------- | ---------------------------------------------------------------------- |
| App     | `apps/ptlam_agent_os/`            | Features and packages | `main`, theme, router, dependency wiring, app-only screens, end-to-end |
| Feature | `features/ptlam_agent_os_<name>/` | Packages only         | One product capability in the four feature layers                      |
| Package | `packages/ptlam_agent_os_<name>/` | Packages only         | One reusable boundary with no product logic; flat `lib/src/`           |

Dependencies point one way: app to feature to package. A feature never imports
another feature. [file-organization.md](references/file-organization.md) owns
the tree; [composition.md](references/composition.md) owns how the app joins
features.

Melos runs every monorepo package from `src/app`:

```bash
melos bootstrap            # after adding a package or a dependency
melos run analyze          # flutter analyze in every package
melos run test             # flutter test in every package with a test/ directory
melos run test:e2e:macos   # the app's end-to-end journeys on macOS
melos run test:e2e:web     # the same journeys through ChromeDriver
```

Run a focused command inside the one package you are changing. Add a Melos
script only when every package needs the same step.

## No code generation

Do not add any package that needs `build_runner` or another code generator,
because every rebuild slows down every agent loop. Write the code a generator
would produce by hand:

| Need                                 | Use                                                                                                                                               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Value equality                       | `equatable` `^3.0.0`; [types-and-data.md](references/types-and-data.md)                                                                           |
| `copyWith`                           | A hand-written method, only where a caller needs it                                                                                               |
| Unions, BLoC events, and BLoC states | Dart 3 `sealed` classes; [models.md](references/models.md), [state-management.md](references/state-management.md)                                 |
| JSON mapping                         | Hand-written `fromJson` and `toJson` on DTOs, with round-trip tests; [models.md](references/models.md)                                            |
| Typed routes                         | Plain `go_router` with path and parameter constants and typed navigation helpers in `app_router.dart`; [widgets.md](references/widgets.md#routes) |
| Mocks                                | `mocktail`; [testing.md](references/testing.md#mocktail-mocks)                                                                                    |
| Translations                         | Hand-written typed string classes plus `flutter_localizations`; [localization.md](references/localization.md)                                     |

These third-party packages stay allowed: `flutter_bloc`, `bloc_concurrency`,
`equatable`, `get_it`, `go_router`, `dio`, `logging`, `shared_preferences`,
`flutter_secure_storage`, `permission_handler`, `bloc_test`, `mocktail`, and
`very_good_analysis`.

## Before review or change

Choose review or change using the foundation's mode policy. In review, use the
installed FVM SDK and the formatter check below, and inspect installed
dependency state without running pub resolution; report missing prerequisites
instead of installing an SDK.

1. Resolve the package root, then read every applicable `AGENTS.md` from the
   repository root down to the files in scope.
2. Resolve the Flutter version through FVM. Run Flutter as `fvm flutter …` and
   Dart as `fvm dart …`; never use a global SDK. Every Dart command named in
   this skill runs through that prefix. A version manager rebinds the SDK per
   project, so run `fvm dart --version` from the package folder.
3. Find out which project you are in:

   | Project  | Version policy                                                                                                          |
   | -------- | ----------------------------------------------------------------------------------------------------------------------- |
   | New      | Latest stable Flutter and latest stable packages                                                                        |
   | Existing | Read `.fvmrc`, `pubspec.yaml`, and `pubspec.lock`, then match them; an upgrade is a separate change with its own checks |

4. Read `pubspec.yaml`, `pubspec.lock`, `analysis_options.yaml`, `.fvmrc`, CI,
   and the nearest source and tests. Note the SDK constraint, resolved
   dependency versions, the included lint set, formatter settings, and the
   commands CI really runs. These files are the project's truth: a rule
   described here that the checked-in configuration does not enable is not
   enforced; report the gap instead of assuming it.
5. For a new single-package project, include
   [`very_good_analysis`](https://pub.dev/packages/very_good_analysis) at its
   pinned version as the lint set. Keep whatever set an existing project uses.
6. Apply the stricter rules to code you add or substantially change. Leave
   unrelated legacy inconsistencies alone.

In the monorepo, also:

1. Confirm `src/app/pubspec.yaml` names `ptlam_agent_os_workspace` and `.fvmrc`
   sits beside it. Work from `src/app`.
2. Read `src/app/README.md`, the root `pubspec.yaml` (pub workspace members and
   Melos scripts), and the `pubspec.yaml` of every package you touch.
3. Keep every package's `ptlam_agent_os_lints` include:
   `analysis_options.flutter.yml` for a Flutter package,
   `analysis_options.dart.yml` for a pure Dart package. Change a rule in the
   lints package, never in one consumer. The set enables
   `always_use_package_imports`, so inside `lib/` write `package:` imports.
4. Name domain types with the binding vocabulary in `agents/002_VISION.md`. Its
   term Workspace is reserved, so call the pub or Melos grouping "the monorepo"
   in code and comments.
5. Record a new third-party dependency or a new package boundary under
   `docs/adrs/` before implementing it (`AGENTS.md`, rule 3); both are hard to
   reverse.

## Pick a reference

| Concern                                                                             | Reference                                                       |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Resolving the SDK, adding a dependency, or reproducing a build                      | [toolchain.md](references/toolchain.md)                         |
| Configuring the analyzer or formatter, or silencing a diagnostic                    | [analysis-options.md](references/analysis-options.md)           |
| Naming a file or symbol, or settling a formatting question                          | [naming-and-formatting.md](references/naming-and-formatting.md) |
| Publishing a library surface, importing, or splitting a library                     | [libraries-and-imports.md](references/libraries-and-imports.md) |
| Declaring a type, a constant, a domain data type, equality, or `copyWith`           | [types-and-data.md](references/types-and-data.md)               |
| Throwing, catching, or translating a failure                                        | [errors.md](references/errors.md)                               |
| Awaiting a `Future`, consuming a `Stream`, or cancelling work                       | [async.md](references/async.md)                                 |
| Placing a layer, defining a repository boundary, or wiring dependencies             | [architecture.md](references/architecture.md)                   |
| Choosing or connecting `setState`, `Cubit`, or `Bloc` state                         | [state-management.md](references/state-management.md)           |
| Adding a file, feature, app, or package; placing a BLoC; choosing what to export    | [file-organization.md](references/file-organization.md)         |
| Registering a monorepo feature's dependencies, or letting one feature reach another | [composition.md](references/composition.md)                     |
| Building a widget, splitting one, declaring a route, or using `BuildContext`        | [widgets.md](references/widgets.md)                             |
| Declaring a monorepo feature route or composing the app router                      | [routing.md](references/routing.md)                             |
| Defining a DTO, a domain entity, a failure, or a sealed union                       | [models.md](references/models.md)                               |
| Calling an external API                                                             | [networking.md](references/networking.md)                       |
| Reading or writing stored data                                                      | [storage.md](references/storage.md)                             |
| Adding or changing user-visible text, or changing the locale                        | [localization.md](references/localization.md)                   |
| Emitting a log record                                                               | [logging.md](references/logging.md)                             |
| Writing a dartdoc comment, documenting a Flutter type, or generating API docs       | [documentation.md](references/documentation.md)                 |
| Choosing a test level, or writing, placing, or running a test                       | [testing.md](references/testing.md)                             |

## Do the work

1. Keep every changed public declaration inside the SDK constraint in
   `pubspec.yaml` and inside what `pubspec.lock` supplies.
2. Give each changed public declaration an explicit type and a doc comment, with
   no `dynamic` in its signature.
3. Await or explicitly hand off every `Future`; cancel every stream subscription
   its owner opened.
4. Add or update behavior tests under `test/` in files ending `_test.dart`. The
   runner finds no other filename.
5. Run checks from narrow to broad and read each result before widening:

   ```bash
   fvm flutter test test/orders_test.dart
   fvm dart analyze lib/orders.dart
   fvm dart format --output=none --set-exit-if-changed .
   fvm flutter analyze
   fvm flutter test
   ```

   In the monorepo, run the focused commands inside the owning package, then
   `melos run analyze` and `melos run test` from `src/app`.

6. In change mode, format the scoped files with `fvm dart format` before
   checking. When you touched `pubspec.yaml`, rerun `fvm dart pub get` (or
   `melos bootstrap` in the monorepo) and commit the pubspec with its lockfile
   wherever the package tracks one.

Inspect the diff after `dart format` or `dart fix --apply`; both rewrite files.
Report the exact commands, their results, the analyzer exclusions that limit
your confidence, and every check you did not run.

## A check failed: where to look

| Failing check                                                         | Reference                                                                                          |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `fvm flutter analyze`, a `very_good_analysis` lint                    | [analysis-options.md](references/analysis-options.md)                                              |
| `fvm dart format` reports a diff                                      | [naming-and-formatting.md](references/naming-and-formatting.md)                                    |
| `use_build_context_synchronously` fires after an `await`              | [widgets.md](references/widgets.md)                                                                |
| Two equal values compare unequal, or a `blocTest` state never matches | [types-and-data.md](references/types-and-data.md), then [models.md](references/models.md)          |
| A `switch` over a union reports a missing case                        | [models.md](references/models.md)                                                                  |
| A DTO round-trip test fails                                           | [models.md](references/models.md#write-the-json-mapping-by-hand)                                   |
| A route or navigation helper is undefined                             | [widgets.md](references/widgets.md#routes), or [routing.md](references/routing.md) in the monorepo |
| A string member is missing in one locale class                        | [localization.md](references/localization.md)                                                      |
| A mocktail `any()` needs a fallback value, or a stub returns `null`   | [testing.md](references/testing.md#mocktail-mocks)                                                 |
| Flutter or Dart SDK constraint mismatch                               | [Before review or change](#before-review-or-change)                                                |
| `pumpAndSettle` times out, or a `blocTest` expectation never arrives  | [testing.md](references/testing.md)                                                                |
| `melos` or pub workspace resolution fails                             | [file-organization.md](references/file-organization.md#adding-a-feature-or-package)                |

## Finish

1. List every foundation reference you read in the handoff.
2. Confirm the change meets the criteria below.

Finish when no package that needs `build_runner` or another generator was added;
touched feature code sits under its `application/`, `domain/`,
`infrastructure/`, or `presentation/` layer and follows its reference;
`fvm flutter analyze` (or `melos run analyze` in the monorepo) reports no new
diagnostic in changed code and
`fvm dart format --output=none --set-exit-if-changed .` reports no difference;
in the monorepo, every import follows the app-to-feature-to-package direction;
the affected tests, and in the monorepo the affected end-to-end journey, pass
under the project's SDK; every remaining suppression has a reason; and the
handoff names each check you could not run.
