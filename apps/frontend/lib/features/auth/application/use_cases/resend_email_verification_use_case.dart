import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Requests another email verification code.
final class const ResendEmailVerificationUseCase(
  final AuthRepository _authRepository,
) {
  /// Creates the use case.
  this;

  /// Requests another code for [email].
  Future<void> invoke(EmailAddress email) =>
      _authRepository.resendEmailVerification(email);
}
