# Dart Types, Constants, and Data Classes

Which Dart keyword carries a value, and how a domain type spells equality,
exhaustiveness, and copying.

## Bind with `final`, and reach for `const`

| Keyword | Use for                                             |
| ------- | --------------------------------------------------- |
| `const` | A value the compiler can build, shared at every use |
| `final` | A binding assigned once at runtime                  |
| `var`   | A binding that really gets reassigned               |

Default to `final` for every local, parameter, and field. Promote to `const`
wherever the analyzer accepts it. A `const` constructor requires every field to
be `final`; the analyzer reports `const_constructor_with_non_final_field`
otherwise. That constraint is how Dart proves the value cannot change.

## Annotate the surface, infer the inside

Declare the parameter and return types of every public declaration, and the type
of every field. Omit the annotation on a local whose initializer already states
it (`omit_local_variable_types`).

Never write `dynamic`. It disables every check the analyzer could make. When a
value is really unknown, type it `Object?` and narrow it where you read it:

```dart
final Object? raw = payload['total'];
if (raw is num) {
  return Money(raw.toInt(), 'EUR');
}
```

Use `?` only where absence is a real state of the domain. A nullable type
obliges every reader to answer for the null, so prefer an empty collection to a
nullable one.

## Close the hierarchy with a class modifier

| Modifier    | Says                                                                 |
| ----------- | -------------------------------------------------------------------- |
| `sealed`    | Every subtype is in this library, so a `switch` over it is checkable |
| `final`     | No one may extend, implement, or mix in this class                   |
| `interface` | Others may implement it, not extend it                               |
| `base`      | Every subtype must itself be `base`, `final`, or `sealed`            |

Make a closed set of states a `sealed` class and match it with a `switch`
expression with no default branch. The analyzer then reports
`non_exhaustive_switch_expression` wherever a new variant must be handled:

```dart
sealed class Shape {}

final class Circle extends Shape {}

final class Square extends Shape {}

String describe(Shape shape) => switch (shape) {
  Circle() => 'circle',
  Square() => 'square',
};
```

A default branch or a `_` wildcard throws that check away.

Use an `enum` for a closed vocabulary with no per-variant data. An enhanced enum
carries fields, a `const` constructor, and methods, which covers a fixed lookup
table. Reach for `sealed` once a variant needs data the others lack.

## Equality, copying, and anonymous shapes

Override `==` and `hashCode` together (`hash_and_equals` fails either one
alone), and only on a type annotated `@immutable` from `package:meta`
(`avoid_equals_and_hash_code_on_mutable_classes`). Build the hash with
`Object.hash(a, b, …)` or `Object.hashAll`.

Give a value type a `copyWith` whose parameters are all named and nullable, so a
caller names only what changes. Say in the doc comment what an omitted argument
does, because `amount ?? this.amount` cannot tell "not passed" from "explicitly
null"; when a field must be settable to null, give it its own sentinel
parameter.

Use a record, such as `(int, String)`, for an anonymous multi-value return that
never leaves the library. Give the shape a named type the moment it crosses a
public boundary or gains a rule.

Get value equality from [`equatable`](https://pub.dev/packages/equatable)
`^3.0.0`: extend `Equatable` and list every field in `props`, so `==` and
`hashCode` cannot drift apart. Write `copyWith` by hand only where a caller
needs it, and model a union with a Dart 3 `sealed` class. Do not use a
data-class generator; [SKILL.md](../SKILL.md#no-code-generation) owns that rule.

## Finish

Finish when every binding you added is `final` or `const`, no signature mentions
`dynamic`, each closed state set is `sealed` and matched without a default
branch, and every type overriding `==` also overrides `hashCode` and is
immutable.
