import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';

/// Watches credential availability for transparent session revocation.
final class const WatchAuthenticationStatusUseCase(
  final AuthRepository _authRepository,
) {
  /// Creates the use case.
  this;

  /// Emits credential availability changes from the auth boundary.
  Stream<AuthenticationStatus> invoke() =>
      _authRepository.watchAuthenticationStatus();
}
