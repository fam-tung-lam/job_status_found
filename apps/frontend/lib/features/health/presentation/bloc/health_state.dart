import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/health/domain/failures/health_failure.dart';
import 'package:job_status_found/features/health/domain/value_objects/health_status.dart';

/// What the health screen knows about the backend.
sealed class const HealthState() extends Equatable {
  /// Creates the state.
  this;

  @override
  List<Object?> get props => const [];
}

/// No check has started yet.
final class const HealthInitial() extends HealthState {
  /// Creates the state.
  this;
}

/// A check is waiting for the backend to answer.
final class const HealthLoading() extends HealthState {
  /// Creates the state.
  this;
}

/// The backend answered with a [status].
final class const HealthLoaded(
  /// The status the backend reported.
  final HealthStatus status,
) extends HealthState {
  /// Creates the state for the backend's reported [status].
  this;

  @override
  List<Object?> get props => [status];
}

/// The last check could not produce a status.
final class const HealthFailed(
  /// Why the check did not produce a status.
  final HealthFailure failure,
) extends HealthState {
  /// Creates the state for the [failure] that ended the check.
  this;

  @override
  List<Object?> get props => [failure];
}
