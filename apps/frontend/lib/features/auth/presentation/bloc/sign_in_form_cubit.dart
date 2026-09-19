import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_state.dart';

/// Submits password sign-in and updates the app session.
final class SignInFormCubit(
  final SignInWithPasswordUseCase _signIn,
  final void Function(SignedInUser user) _setSignedInUser,
) extends Cubit<SignInFormState> {
  /// Creates an editable form cubit.
  this : super(const SignInFormEditing());

  /// Submits one sign-in request, ignoring a concurrent submit.
  Future<void> submit({
    required EmailAddress email,
    required String password,
    required bool rememberMe,
  }) async {
    if (state is SignInFormSubmitting) return;
    emit(const SignInFormSubmitting());
    try {
      final user = await _signIn.invoke(
        email: email,
        password: password,
        rememberMe: rememberMe,
      );
      _setSignedInUser(user);
    } on AuthRejected catch (failure) {
      if (failure.code == AuthRejectionCode.emailVerificationRequired) {
        emit(
          SignInFormEmailVerificationRequired(
            email,
            password,
            rememberMe
                ? SessionPersistence.remembered
                : SessionPersistence.browserSession,
          ),
        );
      } else {
        emit(SignInFormRejected(failure));
      }
    } on AuthFailure catch (failure) {
      emit(SignInFormRejected(failure));
    }
  }
}
