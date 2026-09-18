import 'package:flutter/widgets.dart';
import 'package:job_status_found/features/localization/i18n/health_strings.dart';
import 'package:job_status_found/features/localization/i18n/home_strings.dart';

/// Every user-visible string in the app, grouped by feature.
sealed class const AppStrings() {
  /// Creates the strings.
  this;

  /// Returns the strings for the locale active at [context].
  ///
  /// Requires an `AppStringsDelegate` in the ancestor `MaterialApp`'s
  /// `localizationsDelegates`.
  static AppStrings of(BuildContext context) =>
      Localizations.of<AppStrings>(context, AppStrings)!;

  /// The app name shown by the operating system.
  String get appTitle;

  /// Text shown by the backend health status view.
  HealthStrings get health;

  /// Text shown on the home page.
  HomeStrings get home;
}

/// English [AppStrings].
final class const EnAppStrings() extends AppStrings {
  /// Creates the English strings.
  this;

  @override
  String get appTitle => 'Job Status Found';

  @override
  HealthStrings get health => const EnHealthStrings();

  @override
  HomeStrings get home => const EnHomeStrings();
}
