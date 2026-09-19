import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_state.dart';
import 'package:job_status_found/features/auth/presentation/widgets/auth_switch_prompt.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Email and password sign-in fields and actions.
class const EmailSignInForm({
  /// Email carried from sign-up.
  required final String initialEmail,

  /// Opens sign-up with the current email.
  required final ValueChanged<String> onRegister,

  /// Whether this platform offers cookie-session persistence.
  final bool showRememberDevice = kIsWeb,
  super.key,
}) extends StatefulWidget {
  /// Creates the sign-in form.
  this;

  @override
  State<EmailSignInForm> createState() => _EmailSignInFormState();
}

/// Owns editable field values and validation visibility.
class _EmailSignInFormState() extends State<EmailSignInForm> {
  /// Email input.
  late final TextEditingController _email = TextEditingController(
    text: widget.initialEmail,
  );

  /// Password input.
  final TextEditingController _password = TextEditingController();

  /// Whether the first submit exposed inline errors.
  bool _hasSubmitted = false;

  /// Web persistence choice.
  bool _rememberMe = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  /// Submits valid values or exposes validation errors.
  Future<void> _submit() async {
    setState(() => _hasSubmitted = true);
    final emailAddress = _emailAddress;
    if (emailAddress == null || _passwordError != null) return;
    final cubit = context.read<SignInFormCubit>();
    await cubit.submit(
      email: emailAddress,
      password: _password.text,
      rememberMe: !widget.showRememberDevice || _rememberMe,
    );
    if (cubit.state is SignInFormSubmitting) TextInput.finishAutofillContext();
  }

  /// Current email validation message.
  String? get _emailError {
    if (!_hasSubmitted) return null;
    if (_emailAddress == null) {
      return AppStrings.of(context).auth.invalidEmail;
    }
    return null;
  }

  /// The valid current email, or `null` while its syntax is invalid.
  EmailAddress? get _emailAddress => EmailAddress.tryParse(_email.text);

  /// Current password validation message.
  String? get _passwordError => _hasSubmitted && _password.text.isEmpty
      ? AppStrings.of(context).auth.passwordRequired
      : null;

  @override
  Widget build(
    BuildContext context,
  ) => BlocConsumer<SignInFormCubit, SignInFormState>(
    listener: (_, state) {
      if (state is SignInFormRejected) _password.clear();
    },
    builder: (context, state) {
      final strings = AppStrings.of(context).auth;
      final isSubmitting = state is SignInFormSubmitting;
      final failureMessage = state is SignInFormRejected
          ? _failureMessage(strings, state.failure)
          : null;
      return AutofillGroup(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          spacing: AppSpacing.lg,
          children: [
            AppLabeledDivider(label: strings.signInDivider),
            AppTextField(
              label: strings.emailAddress,
              placeholder: strings.emailAddress,
              controller: _email,
              enabled: !isSubmitting,
              autofillHints: const [AutofillHints.email],
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              autocorrect: false,
              errorText: _emailError,
              onChanged: (_) {
                if (_hasSubmitted) setState(() {});
              },
            ),
            AppTextField(
              label: strings.password,
              placeholder: strings.password,
              controller: _password,
              enabled: !isSubmitting,
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
            if (widget.showRememberDevice)
              Row(
                children: [
                  SizedBox.square(
                    dimension: AppSizes.controlXxl,
                    child: Checkbox(
                      value: _rememberMe,
                      onChanged: isSubmitting
                          ? null
                          : (value) =>
                                setState(() => _rememberMe = value ?? false),
                    ),
                  ),
                  Expanded(child: Text(strings.rememberDevice)),
                  Tooltip(
                    message: strings.rememberDeviceHelp,
                    triggerMode: TooltipTriggerMode.tap,
                    child: const SizedBox.square(
                      dimension: AppSizes.controlXxl,
                      child: Icon(Icons.help_outline),
                    ),
                  ),
                ],
              ),
            if (failureMessage != null)
              AppAlert(title: failureMessage, variant: AppAlertVariant.error),
            AppButton(
              label: strings.signIn,
              onPressed: isSubmitting ? null : _submit,
              isLoading: isSubmitting,
              size: AppButtonSize.xxl,
            ),
            AuthSwitchPrompt(
              prompt: strings.signInSwitchPrefix,
              actionLabel: strings.signInSwitchAction,
              onPressed: isSubmitting
                  ? null
                  : () => widget.onRegister(_email.text.trim()),
            ),
          ],
        ),
      );
    },
  );

  /// Maps one domain failure to localized copy.
  String _failureMessage(AuthStrings strings, AuthFailure failure) =>
      switch (failure) {
        AuthRejected(code: AuthRejectionCode.invalidCredentials) =>
          strings.invalidCredentials,
        AuthRejected(code: AuthRejectionCode.accountUnavailable) =>
          strings.accountUnavailable,
        AuthRejected(
          code: AuthRejectionCode.tooManyAttempts,
          :final retryAfterSeconds,
        ) =>
          strings.tooManyAttempts(((retryAfterSeconds ?? 60) / 60).ceil()),
        _ => strings.serverUnreachable,
      };
}
