# Frontend agent notes

## SDK

- Run every Flutter and Dart command through FVM: `fvm flutter ...` and
  `fvm dart ...`. Never use a global SDK.
- `.fvmrc`, `pubspec.yaml`, and `pubspec.lock` are the source of truth. An SDK
  or package upgrade is a separate change with its own checks.

## No code generation

Do not add any package that needs `build_runner` or another code generator.
Rebuilds slow down every edit-and-check loop. For example, use these instead:

| Need                   | Use                                                                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Value equality         | `equatable`, plus a hand-written `copyWith` where needed                                                                           |
| Unions, events, states | Dart 3 `sealed` classes with exhaustive `switch`                                                                                   |
| JSON                   | Hand-written `fromJson` on DTOs the app reads, `toJson` on DTOs it sends; a round-trip test only for a DTO it both reads and sends |
| Routing                | Plain `go_router` with path and parameter constants                                                                                |
| Test doubles           | `mocktail`                                                                                                                         |
| Localization           | Own `sealed` strings class with one subclass per language                                                                          |

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
- All visual values come from `lib/packages/job_status_found_design_system/`,
  imported from `job_status_found_design_system.dart`, never from `src/`. Its
  `README.md` maps the folder. `lib/app/app.dart` installs `AppTheme.light`
  and `AppTheme.dark`. A feature reads colors from `AppColors.of(context)` and
  distances, radii, text styles, shadows, and durations from the tokens, such
  as `AppSpacing`. A `Color(0x…)`, `Colors.*`, `TextStyle(...)`, or bare
  padding number in a feature is a defect; add the missing value to the design
  system instead. That folder imports nothing else from the app.
- A widget two features render goes in the design system's `src/components/`
  as `App<Name>`, with a preview in `src/previews/` and a test.

## Structure

- `lib/app/` holds `app.dart`, `app_router.dart`, `di.dart`, and
  `app_settings.dart` with `AppSettings`. `app_router.dart` keeps one
  `<Page>Route` constants class per page, such as `HomeRoute`.
- A page is a routed screen with its own `Scaffold`: `<Name>Page` in
  `presentation/pages/<name>_page.dart` of the feature that owns the screen.
  `HomePage` in the `home` feature is the start page.
- A feature shares UI with other features as a widget in
  `presentation/widgets/`, such as `HealthStatusView`, which `HomePage`
  composes. A widget does not build a `Scaffold`.
- `lib/` code imports another feature only through its barrel
  `lib/features/<name>/<name>.dart`.
- A cubit is `<Subject>Cubit` and its sealed state is `<Subject>State`, such as
  `HealthStatusCubit` and `HealthStatusState`. State variants follow the root
  naming rule: `HealthStatusNotChecked`, `HealthStatusChecking`,
  `HealthStatusHealthy`, and `HealthStatusCheckFailed`.
- Failures are sealed classes in `domain/failures/` that implement
  `Exception`.
- Each user-visible string group has its own sealed class in
  `lib/features/localization/i18n/`, such as `HealthStrings` and
  `HomeStrings`, reached through `AppStrings`.

## Code

- Each feature that registers dependencies has `lib/features/<name>/di.dart`
  with a `<name>FeatureScopeName` constant and a `GetIt` extension method
  `push<Name>FeatureScope(AppSettings settings)`, such as
  `pushHealthFeatureScope`. The method pushes a final scope named by the
  constant and registers only that feature's dependencies in its `init`. The
  feature's `<name>.dart` exports both. `lib/app/di.dart` registers shared
  packages in the base scope, then pushes each feature's scope.
- Names follow the root naming rules. A method names what it does to which
  value, such as `HealthRepository.checkBackendHealth()`, never a bare
  `check()`. `JobStatusFoundHttpClient.get(path)` keeps its HTTP method name.
  A private field that holds a collaborator names that collaborator, such as
  `_healthApiClient`, not `_client`. Keep the names Flutter requires, such as
  `build`, `createState`, and `props`.
- Lints come from `very_good_analysis` in `analysis_options.yaml`. Fix the
  code instead of adding `// ignore:`.
- `analysis_options.yaml` adds `use_primary_constructors` and
  `use_declaring_parameters`: declare the constructor in the class header,
  such as
  `final class const HealthStatusCheckFailed(final HealthCheckFailure failure)`,
  and document it on a `this;` body. `fvm dart fix --apply .` converts older code.
- Every public member has a dartdoc comment (`public_member_api_docs`).
- Every private class, constructor, method, function, field, and declaring
  parameter, in `lib/` and `test/`, also has a concise `///` comment. It says
  what the declaration is for, so a reader understands it without reading the
  body. No lint checks this, so check it in review.
- Tests live in `test/{unit,widget,integration}/` followed by the file's path
  under `lib/`, as `<file>_test.dart`, such as
  `test/integration/features/health/presentation/widgets/health_status_view_test.dart`.
- Shared test doubles live in `test/test_doubles/` and shared helpers in
  `test/helpers/`; both serve every level.
- Acquire and release test resources in `setUp`, `tearDown`, `setUpAll`, and
  `tearDownAll`. Never use `addTearDown`.
- Create every mock with `mocktail`; never hand-write a fake or stub class.
- A helper, as the root `AGENTS.md` defines it, is one top-level function in
  `lib/features/<name>/<layer>/helpers/<verb>_<noun>.dart`, such as
  `hashPassword` in `hash_password.dart`. A class takes it as a function-typed
  constructor parameter, and a test passes a closure that returns what the
  case needs instead of a mocktail mock.
- In a local integration test, mock only the lowest API outside our control,
  such as `JobStatusFoundHttpClient` or a storage plugin. Never mock a
  repository, use case, or feature client; run them for real.

## Checks

```shell
fvm flutter analyze
fvm dart format --output=none --set-exit-if-changed .
fvm flutter test
```
