import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Confirms the emailed code and opens a session.
final class const ConfirmEmailVerificationUseCase(
  final AuthRepository _authRepository,
) {
  /// Creates the use case.
  this;

  /// Confirms email ownership with the code and matching password.
  Future<SignedInUser> invoke({
    required EmailAddress email,
    required String code,
    required String password,
    required bool rememberMe,
  }) => _authRepository.confirmEmailVerification(
    email: email,
    code: code,
    password: password,
    rememberMe: rememberMe,
  );
}
