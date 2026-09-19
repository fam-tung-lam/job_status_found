import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

/// Submission state of the sign-up form.
sealed class const SignUpFormState() extends Equatable {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => const [];
}

/// The form accepts edits.
final class const SignUpFormEditing() extends SignUpFormState {
  /// Creates the state.
  this;
}

/// A sign-up request is running.
final class const SignUpFormSubmitting() extends SignUpFormState {
  /// Creates the state.
  this;
}

/// Sign-up failed with [failure].
final class const SignUpFormRejected(final AuthFailure failure)
    extends SignUpFormState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [failure];
}

/// The accepted sign-up moved to verification.
final class const SignUpFormVerificationRequired(
  final EmailAddress email,
  final String password,
) extends SignUpFormState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [email, password];
}
