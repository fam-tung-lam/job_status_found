import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_state.dart';

/// Holds the backend health shown on screen.
///
/// Starts in [HealthStatusNotChecked]. Each [checkBackendHealth] emits
/// [HealthStatusChecking], then [HealthStatusHealthy] or
/// [HealthStatusCheckFailed]. The widget that creates it closes it.
final class HealthStatusCubit(
  /// Performs each backend health check.
  final CheckHealthUseCase _checkHealthUseCase,
) extends Cubit<HealthStatusState> {
  /// Creates the cubit over the use case that performs each check.
  this : super(const HealthStatusNotChecked());

  /// Checks the backend, ignoring the call while a check is in flight.
  ///
  /// A result that arrives after [close] is dropped, because nothing observes
  /// it any more.
  Future<void> checkBackendHealth() async {
    if (state is HealthStatusChecking) return;
    emit(const HealthStatusChecking());
    final result = await _runOneHealthCheck();
    if (!isClosed) emit(result);
  }

  /// Runs one check and returns [HealthStatusHealthy], or
  /// [HealthStatusCheckFailed] with the [HealthCheckFailure] that ended it.
  Future<HealthStatusState> _runOneHealthCheck() async {
    try {
      await _checkHealthUseCase.invoke();
      return const HealthStatusHealthy();
    } on HealthCheckFailure catch (failure) {
      return HealthStatusCheckFailed(failure);
    }
  }
}
