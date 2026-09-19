import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Submission state of the password sign-in form.
sealed class const SignInFormState() extends Equatable {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => const [];
}

/// The form accepts edits.
final class const SignInFormEditing() extends SignInFormState {
  /// Creates the state.
  this;
}

/// A sign-in request is running.
final class const SignInFormSubmitting() extends SignInFormState {
  /// Creates the state.
  this;
}

/// Sign-in failed with [failure].
final class const SignInFormRejected(final AuthFailure failure)
    extends SignInFormState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [failure];
}

/// The email needs verification with the same credentials.
final class const SignInFormEmailVerificationRequired(
  final EmailAddress email,
  final String password,
  final SessionPersistence sessionPersistence,
) extends SignInFormState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [email, password, sessionPersistence];
}

/// Persistence requested for the session verification will create.
enum SessionPersistence() {
  /// The session should end with the browser session.
  browserSession,

  /// The session should persist on this device.
  remembered,
}
