import 'package:equatable/equatable.dart';

/// A health check that could not confirm the backend is healthy.
///
/// Each variant names what the user can do about it.
sealed class const HealthCheckFailure() extends Equatable implements Exception {
  /// Creates the failure.
  this;

  @override
  List<Object?> get props => const [];
}

/// The backend did not answer, so it is probably not running or not reachable
/// at the configured URL.
final class const HealthCheckBackendUnreachableFailure()
    extends HealthCheckFailure {
  /// Creates the failure.
  this;
}

/// The backend answered with a status or body this app does not understand,
/// so the app and backend versions probably disagree.
final class const HealthCheckUnexpectedResponseFailure()
    extends HealthCheckFailure {
  /// Creates the failure.
  this;
}
