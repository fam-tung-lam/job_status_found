import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// The root widget: theme, localization, and routing.
class const App({
  /// Selects the page for the current location. The caller owns its lifetime.
  required final GoRouter router,
  super.key,
}) extends StatelessWidget {
  /// Creates the app around the [router] that selects each page.
  this;

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      onGenerateTitle: (context) => AppStrings.of(context).appTitle,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      localizationsDelegates: const [AppStringsDelegate()],
      supportedLocales: AppStringsDelegate.supportedLocales,
      routerConfig: router,
    );
  }
}
