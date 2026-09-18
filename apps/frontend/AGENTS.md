# Frontend agent notes

## SDK

- Run every Flutter and Dart command through FVM: `fvm flutter ...` and
  `fvm dart ...`. Never use a global SDK.
- `.fvmrc`, `pubspec.yaml`, and `pubspec.lock` are the source of truth. An SDK
  or package upgrade is a separate change with its own checks.

## No code generation

Do not add any package that needs `build_runner` or another code generator.
Rebuilds slow down every edit-and-check loop. For example, use these instead:

| Need                   | Use                                                                 |
| ---------------------- | ------------------------------------------------------------------- |
| Value equality         | `equatable`, plus a hand-written `copyWith` where needed            |
| Unions, events, states | Dart 3 `sealed` classes with exhaustive `switch`                    |
| JSON                   | Hand-written `fromJson` and `toJson` on DTOs, with round-trip tests |
| Routing                | Plain `go_router` with path and parameter constants                 |
| Test doubles           | `mocktail`                                                          |
| Localization           | Own `sealed` strings class with one subclass per language           |

Localization rules:

- Declare every user-visible string once as an abstract getter or method on a
  `sealed` strings class, for example `AppStrings`.
- Give each language one subclass in the same library, for example
  `EnAppStrings`. The compiler then fails when a language misses a string.
- Pass values through method parameters, such as `String greeting(String name)`,
  instead of concatenating strings in widgets.
- Widgets read strings from the abstraction, never from a subclass or a
  literal.

## Dependencies

- Runtime: `flutter_bloc`, `bloc_concurrency`, `equatable`, `get_it`,
  `go_router`, `dio`, `logging`, `shared_preferences`,
  `flutter_secure_storage`.
- Dev: `bloc_test`, `mocktail`, `very_good_analysis`.
- Add `permission_handler` only with the first feature that needs a platform
  permission, together with its iOS and Android setup.
- Add packages with `fvm flutter pub add`. Never edit `pubspec.lock` by hand.
- Only `lib/packages/job_status_found_http_client/` imports `dio`. Other code
  calls the backend through its `JobStatusFoundHttpClient` and handles its
  sealed `JobStatusFoundHttpClientException`, imported from
  `job_status_found_http_client.dart`, never from `src/`. That folder imports
  nothing else from the app, so it can become its own package.

## Code

- Each feature has `lib/features/<name>/di.dart` with a `<name>FeatScopeName`
  constant and a `GetIt` extension method
  `push<Name>FeatScope(AppSettings settings)`, such as `pushHealthFeatScope`.
  The method pushes a final scope named by the constant and registers only
  that feature's dependencies in its `init`. The feature's `<name>.dart`
  exports both. `lib/app/di.dart` registers shared packages in the base scope,
  then pushes each feature's scope.
- Lints come from `very_good_analysis` in `analysis_options.yaml`. Fix the
  code instead of adding `// ignore:`.
- `analysis_options.yaml` adds `use_primary_constructors` and
  `use_declaring_parameters`: declare the constructor in the class header,
  such as `final class const HealthLoaded(final HealthStatus status)`, and
  document it on a `this;` body. `fvm dart fix --apply .` converts older code.
- Every public member has a dartdoc comment (`public_member_api_docs`).
- Every private class, constructor, method, function, field, and declaring
  parameter, in `lib/` and `test/`, also has a concise `///` comment. It says
  what the declaration is for, so a reader understands it without reading the
  body. No lint checks this, so check it in review.
- Tests follow Given-When-Then with explicit `// Given:`, `// When:`, and
  `// Then:` comments.
- Acquire and release test resources in `setUp`, `tearDown`, `setUpAll`, and
  `tearDownAll`. Never use `addTearDown`.
- Create every mock with `mocktail`; never hand-write a fake or stub class.
- In a local integration test, mock only the lowest API outside our control,
  such as `JobStatusFoundHttpClient` or a storage plugin. Never mock a
  repository, use case, or feature client; run them for real.

## Checks

```shell
fvm flutter analyze
fvm dart format --output=none --set-exit-if-changed .
fvm flutter test
```
