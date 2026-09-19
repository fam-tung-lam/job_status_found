import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Opens a session with an email and password.
final class const SignInWithPasswordUseCase(
  final AuthRepository _authRepository,
) {
  /// Creates the use case.
  this;

  /// Signs in with the submitted credentials.
  Future<SignedInUser> invoke({
    required EmailAddress email,
    required String password,
    required bool rememberMe,
  }) => _authRepository.signInWithPassword(
    email: email,
    password: password,
    rememberMe: rememberMe,
  );
}
