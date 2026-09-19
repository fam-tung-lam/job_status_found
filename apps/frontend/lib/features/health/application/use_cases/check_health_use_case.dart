import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';

/// Checks whether the backend can serve requests.
final class const CheckHealthUseCase(
  /// Answers each health check.
  final HealthRepository _healthRepository,
) {
  /// Creates the use case over the [HealthRepository] that answers it.
  this;

  /// Completes normally when the backend is healthy.
  ///
  /// Throws a [HealthCheckFailure] when the backend is unreachable or answers
  /// with something this app does not understand.
  Future<void> invoke() => _healthRepository.checkBackendHealth();
}
