# DTOs, Entities, and Failures

How data crosses a layer: DTOs, domain entities, unions, and failures.

## A DTO is not a domain entity

A DTO mirrors an external shape, such as a JSON body or a stored record, field
for field, including the parts you dislike. A domain entity says what the
application means, in the domain's words.

Keep them separate from the first version. Flutter is stricter here than the
general rule of splitting once the shapes disagree: a vendor owns the wire shape
and can change it in a release you do not control.

## Write the JSON mapping by hand

Give each DTO a `factory OrderResponseDto.fromJson(Map<String, Object?> json)`
and a `Map<String, Object?> toJson()`. Read each field by its wire name and cast
it to the declared type, so a wrong shape fails at the boundary. Keep a wire
name that differs from the Dart name in the string key; do not rename the Dart
field to match. Domain entities carry no serialization code.

Cover each DTO with a round-trip test: `fromJson(dto.toJson())` equals `dto`,
and a recorded wire sample decodes to the expected DTO. Do not use a JSON
generator; [SKILL.md](../SKILL.md#no-code-generation) owns that rule.

## Value objects carry meaning without identity

Put an immutable domain value such as an email address, a money amount, or a
date range under `features/<name>/domain/value_objects/` when it owns validation
or behavior. Compare it by value. Do not create one merely to wrap a primitive;
it earns its place when it prevents an invalid value, names a concept, or owns a
rule.

## Immutable data without a generator

Extend [`Equatable`](https://pub.dev/packages/equatable) `^3.0.0` for DTOs,
entities, BLoC events, and BLoC states, and list every field in `props`. Write
`copyWith` by hand only where a caller needs it;
[types-and-data.md](types-and-data.md#equality-copying-and-anonymous-shapes)
owns its shape. Model unions, events, and states as Dart 3 `sealed` classes with
`final` subclasses in the same library.
[state-management.md](state-management.md#keep-one-bloc-in-three-files) owns the
file layout for a BLoC's events and states.

```dart
sealed class OrdersState extends Equatable {
  const OrdersState();

  @override
  List<Object?> get props => const [];
}

final class OrdersInitial extends OrdersState {
  const OrdersInitial();
}

final class OrdersLoading extends OrdersState {
  const OrdersLoading();
}

final class OrdersLoaded extends OrdersState {
  const OrdersLoaded(this.orders);

  final List<Order> orders;

  @override
  List<Object?> get props => [orders];
}

final class OrdersFailed extends OrdersState {
  const OrdersFailed(this.failure);

  final OrdersFailure failure;

  @override
  List<Object?> get props => [failure];
}
```

Write domain services, invariants, and validation by hand. `Equatable` owns
equality, not the rules about the data.

## "Not loaded yet" is a state, not a null

A screen with no data yet says so through a variant of the state union, never
through a nullable field on a loaded state. A widget forced to test
`orders == null` cannot tell "still loading" from "loaded, and empty".

## Failures cross the boundary, exceptions do not

Inside infrastructure, code throws whatever its library throws. The adapter
catches those and returns a domain failure: a sealed type the use case and BLoC
can match on. Application and presentation code never see a library exception,
catch `Exception`, or inspect a status code.

Name failures for what the user or caller must do about them: `OrdersOffline`,
`OrdersUnauthorized`, and `OrdersRejected(reason)` as subclasses of the sealed
`OrdersFailure`. `OrdersError500` names the wire, not the decision. Keep one
failure type per feature in `features/<name>/domain/failures/`.
