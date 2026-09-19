import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_state.dart';

/// Submits password registration.
final class SignUpFormCubit(final SignUpWithPasswordUseCase _signUp)
    extends Cubit<SignUpFormState> {
  /// Creates an editable form cubit.
  this : super(const SignUpFormEditing());

  /// Submits one sign-up request, ignoring a concurrent submit.
  Future<void> submit({
    required String firstName,
    required String lastName,
    required EmailAddress email,
    required String password,
  }) async {
    if (state is SignUpFormSubmitting) return;
    emit(const SignUpFormSubmitting());
    try {
      await _signUp.invoke(
        firstName: firstName,
        lastName: lastName,
        email: email,
        password: password,
      );
      emit(SignUpFormVerificationRequired(email, password));
    } on AuthFailure catch (failure) {
      emit(SignUpFormRejected(failure));
    }
  }
}
