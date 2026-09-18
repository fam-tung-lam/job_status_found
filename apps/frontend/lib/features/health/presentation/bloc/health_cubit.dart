import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_failure.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_state.dart';

/// Holds the backend health shown on screen.
///
/// Starts in [HealthInitial]. Each [check] emits [HealthLoading], then
/// [HealthLoaded] or [HealthFailed]. The widget that creates it closes it.
final class HealthCubit(
  /// Performs each backend health check.
  final CheckHealthUseCase _checkHealth,
) extends Cubit<HealthState> {
  /// Creates the cubit over the use case that performs each check.
  this : super(const HealthInitial());

  /// Checks the backend, ignoring the call while a check is in flight.
  ///
  /// A result that arrives after [close] is dropped, because nothing observes
  /// it any more.
  Future<void> check() async {
    if (state is HealthLoading) return;
    emit(const HealthLoading());
    final result = await _checkHealthState();
    if (!isClosed) emit(result);
  }

  /// Runs one check and returns [HealthLoaded] with the reported status, or
  /// [HealthFailed] with the [HealthFailure] that ended it.
  Future<HealthState> _checkHealthState() async {
    try {
      return HealthLoaded(await _checkHealth());
    } on HealthFailure catch (failure) {
      return HealthFailed(failure);
    }
  }
}
