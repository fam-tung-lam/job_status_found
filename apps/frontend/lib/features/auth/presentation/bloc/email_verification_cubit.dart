import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_state.dart';

/// Confirms and resends email verification codes.
final class EmailVerificationCubit(
  final ConfirmEmailVerificationUseCase _confirm,
  final ResendEmailVerificationUseCase _resend,
  final void Function(SignedInUser user) _setSignedInUser,
) extends Cubit<EmailVerificationState> {
  /// Creates verification with the send interval active.
  this : super(const EmailVerificationEditing(60)) {
    _startCountdown();
  }

  /// Timer driving the resend label.
  Timer? _timer;

  /// Confirms one code and matching password.
  Future<void> confirm({
    required EmailAddress email,
    required String code,
    required String password,
    required bool rememberMe,
  }) async {
    if (state is EmailVerificationSubmitting) return;
    emit(EmailVerificationSubmitting(state.resendSeconds));
    try {
      final user = await _confirm.invoke(
        email: email,
        code: code,
        password: password,
        rememberMe: rememberMe,
      );
      _setSignedInUser(user);
    } on AuthFailure catch (failure) {
      emit(EmailVerificationRejected(state.resendSeconds, failure));
    }
  }

  /// Requests a new code once the countdown ends.
  Future<void> resend(EmailAddress email) async {
    if (state.resendSeconds > 0 ||
        state is EmailVerificationSubmitting ||
        state is EmailVerificationResending) {
      return;
    }
    emit(const EmailVerificationResending(0));
    try {
      await _resend.invoke(email);
      emit(const EmailVerificationResent(60));
      _startCountdown();
    } on AuthFailure catch (failure) {
      emit(EmailVerificationRejected(0, failure));
    }
  }

  /// Starts or restarts the 60-second resend countdown.
  void _startCountdown() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (isClosed) return;
      final next = state.resendSeconds - 1;
      if (next <= 0) {
        _timer?.cancel();
        emit(_withResendSeconds(0));
      } else {
        emit(_withResendSeconds(next));
      }
    });
  }

  /// Keeps the current result visible while only the countdown changes.
  EmailVerificationState _withResendSeconds(int seconds) => switch (state) {
    EmailVerificationEditing() => EmailVerificationEditing(seconds),
    EmailVerificationSubmitting() => EmailVerificationSubmitting(seconds),
    EmailVerificationResending() => EmailVerificationResending(seconds),
    EmailVerificationRejected(:final failure) => EmailVerificationRejected(
      seconds,
      failure,
    ),
    EmailVerificationResent() => EmailVerificationResent(seconds),
  };

  @override
  Future<void> close() {
    _timer?.cancel();
    return super.close();
  }
}
