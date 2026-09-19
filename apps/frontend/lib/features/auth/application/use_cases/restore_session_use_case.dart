import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';

/// Restores the current session after app startup.
final class const RestoreSessionUseCase(final AuthRepository _authRepository) {
  /// Creates the use case.
  this;

  /// Returns the current user, or `null` when signed out.
  Future<SignedInUser?> invoke() => _authRepository.restoreSession();
}
