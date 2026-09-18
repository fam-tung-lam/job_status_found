# Composition

How the app registers each feature's dependencies and how one feature reaches
another without importing it. These rules apply only in the monorepo described
in [SKILL.md](../SKILL.md#choose-the-layout); [architecture.md](architecture.md)
owns dependency composition in the single-package layout.

## Each feature registers itself

Each feature exports one register function from `lib/src/<feature>_di.dart`:

```dart
void registerOrdersFeature(GetIt getIt) {
  getIt
    ..registerLazySingleton<OrdersRepository>(
      () => ApiOrdersRepository(getIt<AgentOsApiClient>()),
    )
    ..registerFactory(() => PlaceOrderUseCase(getIt<OrdersRepository>()))
    ..registerFactory(() => OrdersBloc(getIt<PlaceOrderUseCase>()));
}
```

`apps/ptlam_agent_os/lib/app/di.dart` holds every registration the app owns, in
this order:

1. Package-level singletons: the logger, the API client, storage wrappers.
2. Each feature's register function.
3. The join adapters described below.

A register function is composition code and may resolve from the container.
Every other class receives dependencies through its constructor, as
[architecture.md](architecture.md) requires.

## Joining features in the app

A feature knows only packages, so it cannot call, navigate to, or observe
another feature. Declare the need as a port in the requesting feature's
`application/ports/` and let the app fulfill it:

| Need                                  | Feature declares                                               | App supplies in `lib/app/`                               |
| ------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| Open another feature's page           | `abstract class OrdersNavigator { void openTask(TaskId id); }` | An adapter that calls the other feature's exported route |
| Read or change another feature's data | A port in domain words                                         | An adapter over the other feature's exported use case    |
| React to another feature's event      | A `Stream` on a port                                           | An adapter bridging the two features                     |

The app binds each adapter in `di.dart` after both features are registered. When
the joined behavior is itself a product rule, write it as an app-owned use case
under `lib/app/` rather than hiding it in an adapter.

Keep a platform-permission adapter in the feature's infrastructure until a
second feature needs it, then move it to a package.

Finish when every feature registers through its own function, the app's
`di.dart` is the only file that calls them, and every cross-feature need is a
port the app fulfills.
