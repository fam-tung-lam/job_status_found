import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';

/// Submission and resend state of email verification.
sealed class const EmailVerificationState(final int resendSeconds)
    extends Equatable {
  /// Creates a state with the remaining resend delay.
  this;
  @override
  List<Object?> get props => [resendSeconds];
}

/// Verification accepts edits.
final class const EmailVerificationEditing(super.resendSeconds)
    extends EmailVerificationState {
  /// Creates the state.
  this;
}

/// Code confirmation is running.
final class const EmailVerificationSubmitting(super.resendSeconds)
    extends EmailVerificationState {
  /// Creates the state.
  this;
}

/// A resend request is running.
final class const EmailVerificationResending(super.resendSeconds)
    extends EmailVerificationState {
  /// Creates the state.
  this;
}

/// Confirmation failed with [failure].
final class const EmailVerificationRejected(
  super.resendSeconds,
  final AuthFailure failure,
) extends EmailVerificationState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [resendSeconds, failure];
}

/// A resend request completed without revealing account state.
final class const EmailVerificationResent(super.resendSeconds)
    extends EmailVerificationState {
  /// Creates the state.
  this;
}
