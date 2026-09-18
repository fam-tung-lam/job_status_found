# Dartdoc and Flutter Documentation

The syntax Dart uses for a documentation comment and the tools that check it,
then what a doc comment on a Flutter type has to answer beyond the contract
every public declaration owes its caller.

## Write `///`, summary first

Use `///` on every line. `/** */` is legacy and `slash_for_doc_comments` reports
it. Put the comment directly above the declaration, above any annotation.

Open with one sentence that ends in a period and fits on its own line. Dartdoc
lifts that first paragraph into every index and search result, so a summary that
runs three lines shows up cut off everywhere. Leave a blank `///` line before
any further detail. Write the summary in the third person: "Returns the cached
locale."

```dart
/// Places [order] and returns the accepted confirmation.
///
/// Throws [ArgumentError] when [Order.id] is empty, and
/// [OrdersUnavailable] when the service declines the request.
Future<Confirmation> place(Order order) async { … }
```

## Link every symbol you name

Put a symbol in square brackets, such as `[Order]`, `[place]`, or `[Order.id]`,
and dartdoc links it to that declaration's page. Enable `comment_references`; it
reports `The referenced name isn't visible in scope`, which catches a renamed
symbol and a symbol you never imported.

Name each thrown type in brackets too. That is the only way a caller browsing
the generated API sees what it must catch.

## Reuse a block instead of copying it

Define the block once and stamp it wherever it belongs:

```dart
/// {@template orders.retry}
/// Retries up to three times with exponential backoff.
/// {@endtemplate}

/// Fetches the order.
///
/// {@macro orders.retry}
Future<Order> fetch(String id) async { … }
```

`dart doc` expands `{@macro}` into the generated page. Prefix the template name
with the package or library so two packages cannot collide.

## Document the library, not the file

A library-level doc comment needs a `library;` directive below it, or dartdoc
attaches it to whatever declaration follows. The `dangling_library_doc_comments`
lint reports a doc comment left floating.

## Let the tools check it

| Rule                     | Requires                                             |
| ------------------------ | ---------------------------------------------------- |
| `public_member_api_docs` | A doc comment on every public member                 |
| `package_api_docs`       | A doc comment on every declaration a package exports |
| `comment_references`     | Every bracketed name to resolve                      |

Run `dart doc` before publishing anything with a documented surface. It prints a
warning-and-error count and fails on a broken reference.

## Document Flutter types

| Symbol               | Document                                                                            |
| -------------------- | ----------------------------------------------------------------------------------- |
| Widget               | What it renders, what each constructor argument controls, and any required ancestor |
| BLoC or Cubit        | Which events it accepts, which states it emits, and what closes it                  |
| Use case             | The rule it enforces and every failure it can return                                |
| Repository           | Which sources answer, the fallback when one fails, and the failures it returns      |
| Entity or DTO        | What the type means and any renamed wire field                                      |
| Extension or utility | When to use it and when not to                                                      |

A widget's required ancestor is the commonest omission: a widget that reads a
`BlocProvider`, `Theme`, or localization scope throws at runtime when mounted
without one, and only the doc comment warns first.

Say who disposes what. Whenever a constructor accepts a controller, a focus
node, or a subscription, say whether the widget closes it or the caller keeps
that duty.

Finish when every public declaration you touched has a `///` comment whose first
sentence stands alone, every symbol and thrown type it names is bracketed,
`dart doc` reports no new warning, every public widget, state holder, use case,
and repository you touched answers its row, and every lifecycle duty the
signature hides is named.
