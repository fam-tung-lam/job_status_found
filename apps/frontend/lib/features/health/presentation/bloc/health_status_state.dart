import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';

/// What the app knows about the backend's health.
sealed class const HealthStatusState() extends Equatable {
  /// Creates the state.
  this;

  @override
  List<Object?> get props => const [];
}

/// No health check has started yet.
final class const HealthStatusNotChecked() extends HealthStatusState {
  /// Creates the state.
  this;
}

/// A health check is waiting for the backend to answer.
final class const HealthStatusChecking() extends HealthStatusState {
  /// Creates the state.
  this;
}

/// The last health check confirmed that the backend can serve requests.
final class const HealthStatusHealthy() extends HealthStatusState {
  /// Creates the state.
  this;
}

/// The last health check ended with a [failure].
final class const HealthStatusCheckFailed(
  /// Why the check could not confirm the backend is healthy.
  final HealthCheckFailure failure,
) extends HealthStatusState {
  /// Creates the state for the [failure] that ended the check.
  this;

  @override
  List<Object?> get props => [failure];
}
