import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_state.dart';
import 'package:job_status_found/features/auth/presentation/widgets/auth_page_frame.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Routed page that confirms an emailed code and the matching password.
class const EmailVerificationPage({
  required final EmailVerificationCubit emailVerificationCubit,
  required final EmailAddress email,
  required final String initialPassword,
  required final bool rememberMe,
  required final VoidCallback onUseDifferentEmail,
  super.key,
}) extends StatefulWidget {
  /// Creates email verification.
  this;
  @override
  State<EmailVerificationPage> createState() => _EmailVerificationPageState();
}

/// Owns code and password inputs.
class _EmailVerificationPageState() extends State<EmailVerificationPage> {
  /// Six-digit code input.
  final TextEditingController _code = TextEditingController();

  /// Password input, carried only in memory when available.
  late final TextEditingController _password = TextEditingController(
    text: widget.initialPassword,
  );

  /// Focus returned to the code after a failed attempt or resend.
  final FocusNode _codeFocus = FocusNode();

  /// Whether inline validation is visible.
  bool _hasSubmitted = false;

  @override
  void dispose() {
    _code.dispose();
    _password.dispose();
    _codeFocus.dispose();
    super.dispose();
  }

  /// Confirms valid input.
  Future<void> _submit() async {
    setState(() => _hasSubmitted = true);
    if (_codeError != null || _passwordError != null) return;
    await widget.emailVerificationCubit.confirm(
      email: widget.email,
      code: _code.text,
      password: _password.text,
      rememberMe: widget.rememberMe,
    );
  }

  /// Validates exactly six ASCII digits.
  String? get _codeError =>
      _hasSubmitted && !RegExp(r'^\d{6}$').hasMatch(_code.text)
      ? AppStrings.of(context).auth.invalidVerificationCode
      : null;

  /// Requires the password that the backend confirms.
  String? get _passwordError => _hasSubmitted && _password.text.isEmpty
      ? AppStrings.of(context).auth.passwordRequired
      : null;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: BlocProvider(
      create: (_) => widget.emailVerificationCubit,
      child: BlocConsumer<EmailVerificationCubit, EmailVerificationState>(
        listener: (_, state) {
          if (state case EmailVerificationRejected(
            failure: AuthRejected(
              code: AuthRejectionCode.verificationCodeInvalid,
            ),
          )) {
            _code.clear();
            _codeFocus.requestFocus();
          }
          if (state is EmailVerificationResent) {
            _code.clear();
            _codeFocus.requestFocus();
          }
        },
        builder: (context, state) {
          final strings = AppStrings.of(context).auth;
          final isBusy =
              state is EmailVerificationSubmitting ||
              state is EmailVerificationResending;
          final invalid = switch (state) {
            EmailVerificationRejected(
              failure: AuthRejected(
                code: AuthRejectionCode.verificationCodeInvalid,
              ),
            ) =>
              true,
            _ => false,
          };
          return PopScope(
            canPop: !isBusy,
            child: AuthPageFrame(
              headline: strings.checkEmailHeadline,
              subtitle: strings.verificationExplanation(widget.email.asTyped),
              child: AutofillGroup(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  spacing: AppSpacing.lg,
                  children: [
                    AppTextField(
                      label: strings.verificationCode,
                      placeholder: strings.verificationCode,
                      controller: _code,
                      focusNode: _codeFocus,
                      enabled: !isBusy,
                      keyboardType: TextInputType.number,
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.oneTimeCode],
                      maxLength: 6,
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      errorText: _codeError,
                      onChanged: (_) {
                        if (_hasSubmitted) setState(() {});
                      },
                    ),
                    AppTextField(
                      label: strings.password,
                      placeholder: strings.password,
                      controller: _password,
                      enabled: !isBusy,
                      isObscured: true,
                      showObscuredTextTooltip: strings.showPassword,
                      hideObscuredTextTooltip: strings.hidePassword,
                      autofillHints: const [AutofillHints.password],
                      textInputAction: TextInputAction.done,
                      errorText: _passwordError,
                      onChanged: (_) {
                        if (_hasSubmitted) setState(() {});
                      },
                      onSubmitted: (_) => _submit(),
                    ),
                    if (invalid)
                      AppAlert(
                        title: strings.verificationInvalid,
                        variant: AppAlertVariant.error,
                      ),
                    if (state is EmailVerificationRejected && !invalid)
                      AppAlert(
                        title: strings.serverUnreachable,
                        variant: AppAlertVariant.error,
                      ),
                    if (state is EmailVerificationResent)
                      AppAlert(
                        title: strings.verificationResent,
                        variant: AppAlertVariant.info,
                      ),
                    AppButton(
                      label: strings.verifyEmail,
                      onPressed: isBusy ? null : _submit,
                      isLoading: state is EmailVerificationSubmitting,
                      size: AppButtonSize.xxl,
                    ),
                    AppButton(
                      label: state.resendSeconds > 0
                          ? strings.resendCodeIn(state.resendSeconds)
                          : strings.resendCode,
                      variant: AppButtonVariant.ghost,
                      size: AppButtonSize.xxl,
                      isLoading: state is EmailVerificationResending,
                      onPressed: isBusy || state.resendSeconds > 0
                          ? null
                          : () => unawaited(
                              widget.emailVerificationCubit.resend(
                                widget.email,
                              ),
                            ),
                    ),
                    AppButton(
                      label: strings.useDifferentEmail,
                      variant: AppButtonVariant.link,
                      size: AppButtonSize.xxl,
                      onPressed: isBusy ? null : widget.onUseDifferentEmail,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    ),
  );
}
