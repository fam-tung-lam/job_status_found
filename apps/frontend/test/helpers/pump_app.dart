import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Pumps widgets inside the app's theme and localization scope.
extension PumpApp on WidgetTester {
  /// Pumps [page] as the home of a `MaterialApp` that installs the light
  /// [AppTheme] and loads [AppStrings].
  Future<void> pumpApp(Widget page) => pumpWidget(
    MaterialApp(
      theme: AppTheme.light,
      localizationsDelegates: const [AppStringsDelegate()],
      supportedLocales: AppStringsDelegate.supportedLocales,
      home: page,
    ),
  );
}
