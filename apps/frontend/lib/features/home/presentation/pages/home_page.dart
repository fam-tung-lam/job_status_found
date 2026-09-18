import 'package:flutter/material.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// The app's start page, which shows the backend's health for now.
///
/// Requires an `AppStringsDelegate` in the ancestor `MaterialApp`.
class const HomePage({
  /// Performs each backend health check shown on the page.
  required final CheckHealthUseCase checkHealthUseCase,
  super.key,
}) extends StatelessWidget {
  /// Creates the page over the use case that performs each health check.
  this;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(AppStrings.of(context).home.pageTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: HealthStatusView(checkHealthUseCase: checkHealthUseCase),
        ),
      ),
    );
  }
}
