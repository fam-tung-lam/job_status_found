import 'package:job_status_found/features/health/domain/failures/health_failure.dart';
import 'package:job_status_found/features/health/domain/value_objects/health_status.dart';

/// Source of the backend's health status.
abstract interface class HealthRepository() {
  /// Creates the repository.
  this;

  /// Asks the backend whether it can serve requests.
  ///
  /// Throws a [HealthFailure] when the backend is unreachable or answers with
  /// something this app does not understand.
  Future<HealthStatus> check();
}
