# Localization

How user-visible text is declared, translated, and read, then who owns
translations and the active locale across monorepo packages.

Write typed string classes by hand and use the Flutter SDK's
`flutter_localizations` for the framework's own strings. Declare one abstract
`AppStrings` class with one member per message, and give each supported locale
one implementation, such as `AppStringsEn` and `AppStringsVi`. Deliver the
implementation for the active locale through a `LocalizationsDelegate` and read
it with `AppStrings.of(context)`. Do not add a package that generates the
strings; [SKILL.md](../SKILL.md#no-code-generation) owns that rule.

Localization is a feature, not a utility. In the single-package layout it lives
at `lib/features/localization/` with the same four layers as any feature, plus
its string classes under `i18n/`. Its locale BLoC lives in `presentation/bloc/`,
the repository port in `application/ports/`, the implementation in
`infrastructure/adapters/`, storage in `infrastructure/data_sources/`, and
widgets in `presentation/`.

## Every user-visible string is a member

No literal user-visible text in a widget. Add the member to `AppStrings` and
implement it in every supported locale class. Every locale class implements
every member, so a missing translation is a compile error.

Name a member for what the text means, not what it says:
`orders.emptyStateTitle`, not `orders.noOrdersYet`. Group members into one
abstract class per feature and page, reached from `AppStrings`, so an unused
group is visible when its page is deleted.

## Do not build sentences from parts

Pass a parameter into one member. Never join two translated fragments; word
order differs between languages and the result cannot be reviewed. Give anything
counted one member that takes the count, and let each locale class choose its
own plural forms. Put date, time, number, and currency formatting through the
locale-aware formatter, not string interpolation.

## Read a translation in the presentation layer

A BLoC, use case, or adapter emits a key or a domain value; it never emits a
translated sentence, because it has no locale and no `BuildContext`. An error
shown to the user is a failure variant the widget maps to a string member; see
[models.md](models.md).

## Change the locale through state

The locale selection is presentation state: `AppLocaleRepository` persists it
through `AppLocaleLocalDataSource`, a BLoC in this feature owns it, and the app
applies it at the root. Dispatch an event; never call the setter from a page.

## Own translations in the monorepo

These rules apply only in the monorepo described in
[SKILL.md](../SKILL.md#choose-the-layout).

| Owner              | Holds                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| Feature            | `lib/src/i18n/` with its abstract strings class, one class per supported locale, and its delegate |
| App                | The supported locale list, the active locale, and the delegates in `lib/app/app.dart`             |
| A settings feature | The page that lets the operator pick a locale, and the storage that persists it                   |

Every feature that shows text carries its own abstract strings class, named for
the feature, with the same per-locale implementations and delegate the
single-package `AppStrings` uses, so a feature can be deleted with its strings.
Add a member to the owning feature's classes.

The app lists every feature's delegate and the `flutter_localizations` delegates
in `localizationsDelegates`, and applies the active locale at the root at
startup and on change. A feature whose delegate is missing from that list fails
at its first lookup.

The locale is application state. The settings feature persists it through a data
source, a BLoC in that feature owns it, and the app observes that BLoC and
applies the locale at the root.

Finish when no widget holds a literal user-visible string, every locale class
implements every member, no sentence is assembled from fragments, and every
feature that shows text registers its delegate with the app.
