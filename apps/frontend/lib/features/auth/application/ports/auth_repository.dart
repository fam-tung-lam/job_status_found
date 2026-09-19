import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Authenticates people and restores their current session.
abstract interface class AuthRepository() {
  /// Creates an auth repository.
  this;

  /// Restores a stored or cookie-backed session.
  Future<SignedInUser?> restoreSession();

  /// Emits when session credentials become available or are revoked.
  Stream<AuthenticationStatus> watchAuthenticationStatus();

  /// Signs in with an email and password.
  Future<SignedInUser> signInWithPassword({
    required EmailAddress email,
    required String password,
    required bool rememberMe,
  });

  /// Starts email and password registration.
  Future<void> signUpWithPassword({
    required String firstName,
    required String lastName,
    required EmailAddress email,
    required String password,
  });

  /// Confirms email ownership and opens a session.
  Future<SignedInUser> confirmEmailVerification({
    required EmailAddress email,
    required String code,
    required String password,
    required bool rememberMe,
  });

  /// Requests another verification email.
  Future<void> resendEmailVerification(EmailAddress email);
}
