import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_state.dart';
import 'package:job_status_found/features/auth/presentation/widgets/auth_page_frame.dart';
import 'package:job_status_found/features/auth/presentation/widgets/email_sign_in_form.dart';
import 'package:job_status_found/features/localization/localization.dart';

/// Routed password sign-in screen.
class const SignInPage({
  required final SignInFormCubit signInFormCubit,
  required final String initialEmail,
  required final ValueChanged<String> onRegister,
  required final void Function({
    required String email,
    required String password,
    required bool rememberMe,
  })
  onVerificationRequired,
  super.key,
}) extends StatelessWidget {
  /// Creates the sign-in page.
  this;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: BlocProvider(
      create: (_) => signInFormCubit,
      child: BlocListener<SignInFormCubit, SignInFormState>(
        listener: (_, state) {
          if (state case SignInFormEmailVerificationRequired(
            :final email,
            :final password,
            :final sessionPersistence,
          )) {
            onVerificationRequired(
              email: email.asTyped,
              password: password,
              rememberMe: sessionPersistence == SessionPersistence.remembered,
            );
          }
        },
        child: AuthPageFrame(
          headline: AppStrings.of(context).auth.signInHeadline,
          child: EmailSignInForm(
            initialEmail: initialEmail,
            onRegister: onRegister,
          ),
        ),
      ),
    ),
  );
}
