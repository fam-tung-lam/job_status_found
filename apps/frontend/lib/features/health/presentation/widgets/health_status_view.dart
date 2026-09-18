import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_cubit.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_state.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// Shows whether the backend can serve requests, and lets the user check
/// again.
///
/// Checks the backend as soon as it is built. Requires an `AppStringsDelegate`
/// in the ancestor `MaterialApp`.
class const HealthStatusView({
  /// Performs each backend health check.
  required final CheckHealthUseCase checkHealthUseCase,
  super.key,
}) extends StatelessWidget {
  /// Creates the view over the use case that performs each check.
  this;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) {
        final cubit = HealthStatusCubit(checkHealthUseCase);
        // The cubit turns every expected failure into state and drops a late
        // result after close, so the view does not await the first check.
        unawaited(cubit.check());
        return cubit;
      },
      child: BlocBuilder<HealthStatusCubit, HealthStatusState>(
        builder: (context, state) => switch (state) {
          HealthStatusNotChecked() ||
          HealthStatusChecking() => const _CheckInProgress(),
          HealthStatusHealthy() => const _HealthyResult(),
          HealthStatusCheckFailed(:final failure) => _FailureResult(failure),
        },
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

/// The result of a check that confirmed the backend is healthy.
class const _HealthyResult() extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return _CheckResult(
      icon: Icons.check_circle,
      color: Theme.of(context).colorScheme.primary,
      message: AppStrings.of(context).health.statusHealthy,
    );
  }
}

/// The result of a check that ended with a [HealthCheckFailure].
class const _FailureResult(
  /// Why the check could not confirm the backend is healthy.
  final HealthCheckFailure failure,
) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final strings = AppStrings.of(context).health;
    final colors = Theme.of(context).colorScheme;
    return switch (failure) {
      HealthCheckBackendUnreachable() => _CheckResult(
        icon: Icons.cloud_off,
        color: colors.error,
        message: strings.statusUnreachable,
      ),
      HealthCheckUnexpectedResponse() => _CheckResult(
        icon: Icons.error,
        color: colors.error,
        message: strings.statusUnexpectedResponse,
      ),
    };
  }
}

/// A finished check: an icon, a message, and a button that checks again
/// through the [HealthStatusCubit] above it.
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
          onPressed: () => unawaited(context.read<HealthStatusCubit>().check()),
          child: Text(AppStrings.of(context).health.checkAgainAction),
        ),
      ],
    );
  }
}
