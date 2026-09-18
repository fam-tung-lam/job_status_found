import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_failure.dart';
import 'package:job_status_found/features/health/domain/value_objects/health_status.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_cubit.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_state.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// Shows whether the backend can serve requests, and lets the user check
/// again.
///
/// Checks the backend as soon as it is built. Requires an `AppStringsDelegate`
/// in the ancestor `MaterialApp`.
class const HealthPage({
  /// Performs each backend health check.
  required final CheckHealthUseCase checkHealth,
  super.key,
}) extends StatelessWidget {
  /// Creates the page over the use case that performs each check.
  this;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) {
        final cubit = HealthCubit(checkHealth);
        // The cubit turns every expected failure into state and drops a late
        // result after close, so the page does not await the first check.
        unawaited(cubit.check());
        return cubit;
      },
      child: const _HealthView(),
    );
  }
}

/// The health page's scaffold: a title bar and the current check state,
/// read from the [HealthCubit] above it.
class const _HealthView() extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(AppStrings.of(context).health.pageTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: BlocBuilder<HealthCubit, HealthState>(
            builder: (context, state) => switch (state) {
              HealthInitial() || HealthLoading() => const _CheckInProgress(),
              HealthLoaded(:final status) => _StatusResult(status),
              HealthFailed(:final failure) => _FailureResult(failure),
            },
          ),
        ),
      ),
    );
  }
}

/// A spinner with a message, shown while a check waits for the backend.
class const _CheckInProgress() extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      spacing: 16,
      children: [
        const CircularProgressIndicator(),
        Text(AppStrings.of(context).health.checkInProgress),
      ],
    );
  }
}

/// The result of a check that returned a [HealthStatus].
class const _StatusResult(
  /// The status the backend reported.
  final HealthStatus status,
) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final strings = AppStrings.of(context).health;
    final colors = Theme.of(context).colorScheme;
    return switch (status) {
      HealthStatus.ok => _CheckResult(
        icon: Icons.check_circle,
        color: colors.primary,
        message: strings.statusHealthy,
      ),
    };
  }
}

/// The result of a check that ended with a [HealthFailure].
class const _FailureResult(
  /// Why the check did not produce a status.
  final HealthFailure failure,
) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final strings = AppStrings.of(context).health;
    final colors = Theme.of(context).colorScheme;
    return switch (failure) {
      HealthUnreachable() => _CheckResult(
        icon: Icons.cloud_off,
        color: colors.error,
        message: strings.statusUnreachable,
      ),
      HealthUnexpectedResponse() => _CheckResult(
        icon: Icons.error,
        color: colors.error,
        message: strings.statusUnexpectedResponse,
      ),
    };
  }
}

/// A finished check: an icon, a message, and a button that checks again
/// through the [HealthCubit] above it.
class const _CheckResult({
  /// The symbol for the outcome.
  required final IconData icon,

  /// The theme color that marks the outcome as good or bad.
  required final Color color,

  /// The localized sentence that explains the outcome.
  required final String message,
}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      spacing: 16,
      children: [
        Icon(icon, color: color, size: 48),
        Text(message, textAlign: TextAlign.center),
        FilledButton(
          onPressed: () => unawaited(context.read<HealthCubit>().check()),
          child: Text(AppStrings.of(context).health.checkAgainAction),
        ),
      ],
    );
  }
}
