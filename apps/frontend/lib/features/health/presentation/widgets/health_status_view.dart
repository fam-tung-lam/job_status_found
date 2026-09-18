import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_cubit.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_state.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Shows whether the backend can serve requests, and lets the user check
/// again.
///
/// Checks the backend as soon as it is built. Requires an `AppStringsDelegate`
/// and a theme built by `AppTheme` in the ancestor `MaterialApp`.
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
    return Row(
      mainAxisSize: MainAxisSize.min,
      spacing: AppSpacing.sm,
      children: [
        const AppSpinner(),
        Flexible(child: Text(AppStrings.of(context).health.checkInProgress)),
      ],
    );
  }
}

/// The result of a check that confirmed the backend is healthy.
class const _HealthyResult() extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return _CheckResult(
      icon: Icons.check_circle_outline,
      variant: AppAlertVariant.success,
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
    return switch (failure) {
      HealthCheckBackendUnreachable() => _CheckResult(
        icon: Icons.cloud_off_outlined,
        variant: AppAlertVariant.error,
        message: strings.statusUnreachable,
      ),
      HealthCheckUnexpectedResponse() => _CheckResult(
        icon: Icons.error_outline,
        variant: AppAlertVariant.error,
        message: strings.statusUnexpectedResponse,
      ),
    };
  }
}

/// A finished check: an alert with an icon, a message, and a button that
/// checks again through the [HealthStatusCubit] above it.
class const _CheckResult({
  /// The symbol for the outcome.
  required final IconData icon,

  /// The alert look that marks the outcome as good or bad.
  required final AppAlertVariant variant,

  /// The localized sentence that explains the outcome.
  required final String message,
}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return AppAlert(
      icon: icon,
      variant: variant,
      title: message,
      action: AppButton(
        label: AppStrings.of(context).health.checkAgainAction,
        variant: AppButtonVariant.outline,
        size: AppButtonSize.sm,
        onPressed: () => unawaited(context.read<HealthStatusCubit>().check()),
      ),
    );
  }
}
