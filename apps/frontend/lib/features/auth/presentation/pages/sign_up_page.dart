import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_state.dart';
import 'package:job_status_found/features/auth/presentation/widgets/auth_page_frame.dart';
import 'package:job_status_found/features/auth/presentation/widgets/email_sign_up_form.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// Routed email and password registration screen.
class const SignUpPage({
  required final SignUpFormCubit signUpFormCubit,
  required final String initialEmail,
  required final Uri termsUrl,
  required final Uri privacyUrl,
  required final ValueChanged<String> onLogIn,
  required final void Function(String email, String password)
  onVerificationRequired,
  super.key,
}) extends StatelessWidget {
  /// Creates the sign-up page.
  this;
  @override
  Widget build(BuildContext context) => Scaffold(
    body: BlocProvider(
      create: (_) => signUpFormCubit,
      child: BlocListener<SignUpFormCubit, SignUpFormState>(
        listener: (_, state) {
          if (state case SignUpFormVerificationRequired(
            :final email,
            :final password,
          )) {
            onVerificationRequired(email.asTyped, password);
          }
        },
        child: AuthPageFrame(
          headline: AppStrings.of(context).auth.signUpHeadline,
          child: EmailSignUpForm(
            initialEmail: initialEmail,
            termsUrl: termsUrl,
            privacyUrl: privacyUrl,
            onLogIn: onLogIn,
          ),
        ),
      ),
    ),
  );
}
