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

## Code

- Lints come from `very_good_analysis` in `analysis_options.yaml`. Fix the
  code instead of adding `// ignore:`.
- Every public member has a dartdoc comment (`public_member_api_docs`).
- Tests follow Given-When-Then with explicit `// Given:`, `// When:`, and
  `// Then:` comments.

## Checks

```shell
fvm flutter analyze
fvm dart format --output=none --set-exit-if-changed .
fvm flutter test
```
