import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';

/// Source of the backend's health.
abstract interface class HealthRepository() {
  /// Creates the repository.
  this;

  /// Asks the backend whether it can serve requests.
  ///
  /// Completes normally when the backend is healthy. Throws a
  /// [HealthCheckFailure] when the backend is unreachable or answers with
  /// something this app does not understand.
  Future<void> checkBackendHealth();
}
