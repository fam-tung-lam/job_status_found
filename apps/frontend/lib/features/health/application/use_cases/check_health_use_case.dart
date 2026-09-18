import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/domain/failures/health_failure.dart';
import 'package:job_status_found/features/health/domain/value_objects/health_status.dart';

/// Checks whether the backend can serve requests.
final class const CheckHealthUseCase(
  /// Answers each health check.
  final HealthRepository _repository,
) {
  /// Creates the use case over the [HealthRepository] that answers it.
  this;

  /// Returns the backend's current [HealthStatus].
  ///
  /// Throws a [HealthFailure] when the backend is unreachable or answers with
  /// something this app does not understand.
  Future<HealthStatus> call() => _repository.check();
}
