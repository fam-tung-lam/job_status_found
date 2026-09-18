import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// Pumps widgets inside the app's localization scope.
extension PumpApp on WidgetTester {
  /// Pumps [page] as the home of a `MaterialApp` that loads [AppStrings].
  Future<void> pumpApp(Widget page) => pumpWidget(
    MaterialApp(
      localizationsDelegates: const [AppStringsDelegate()],
      supportedLocales: AppStringsDelegate.supportedLocales,
      home: page,
    ),
  );
}
