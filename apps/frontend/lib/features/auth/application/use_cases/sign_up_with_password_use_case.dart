import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Starts registration with names, email, and password.
final class const SignUpWithPasswordUseCase(
  final AuthRepository _authRepository,
) {
  /// Creates the use case.
  this;

  /// Submits a new password account.
  Future<void> invoke({
    required String firstName,
    required String lastName,
    required EmailAddress email,
    required String password,
  }) => _authRepository.signUpWithPassword(
    firstName: firstName,
    lastName: lastName,
    email: email,
    password: password,
  );
}
