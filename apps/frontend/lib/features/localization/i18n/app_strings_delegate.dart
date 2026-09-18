import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:job_status_found/features/localization/i18n/app_strings.dart';

/// Loads the [AppStrings] for the active locale.
final class const AppStringsDelegate()
    extends LocalizationsDelegate<AppStrings> {
  /// Creates the delegate.
  this;

  /// The locales that have an [AppStrings] implementation.
  static const supportedLocales = [Locale('en')];

  @override
  bool isSupported(Locale locale) => supportedLocales.any(
    (supported) => supported.languageCode == locale.languageCode,
  );

  @override
  Future<AppStrings> load(Locale locale) =>
      SynchronousFuture(const EnAppStrings());

  @override
  bool shouldReload(AppStringsDelegate old) => false;
}
