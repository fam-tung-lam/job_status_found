import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_state.dart';
import 'package:job_status_found/features/auth/presentation/widgets/auth_switch_prompt.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';
import 'package:url_launcher/url_launcher.dart';

/// Name, email, and password registration fields and actions.
class const EmailSignUpForm({
  /// Email carried from sign-in.
  required final String initialEmail,

  /// Terms page opened by the legal line.
  required final Uri termsUrl,

  /// Privacy page opened by the legal line.
  required final Uri privacyUrl,

  /// Opens sign-in with the current email.
  required final ValueChanged<String> onLogIn,
  super.key,
}) extends StatefulWidget {
  /// Creates the sign-up form.
  this;

  @override
  State<EmailSignUpForm> createState() => _EmailSignUpFormState();
}

/// Owns editable sign-up values and validation visibility.
class _EmailSignUpFormState() extends State<EmailSignUpForm> {
  /// Given-name input.
  final TextEditingController _firstName = TextEditingController();

  /// Family-name input.
  final TextEditingController _lastName = TextEditingController();

  /// Email input.
  late final TextEditingController _email = TextEditingController(
    text: widget.initialEmail,
  );

  /// Password input.
  final TextEditingController _password = TextEditingController();

  /// Whether validation errors are visible.
  bool _hasSubmitted = false;

  /// Password value sent with the latest rejected request.
  String? _rejectedPassword;

  @override
  void dispose() {
    _firstName.dispose();
    _lastName.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  /// Submits valid values or exposes validation errors.
  Future<void> _submit() async {
    setState(() => _hasSubmitted = true);
    if (_nameError(_firstName.text) != null ||
        _nameError(_lastName.text) != null ||
        _emailAddress == null ||
        _passwordError != null) {
      return;
    }
    _rejectedPassword = null;
    await context.read<SignUpFormCubit>().submit(
      firstName: _firstName.text.trim(),
      lastName: _lastName.text.trim(),
      email: _emailAddress!,
      password: _password.text,
    );
  }

  /// Validates one name.
  String? _nameError(String value) {
    if (!_hasSubmitted) return null;
    if (value.trim().isEmpty) return AppStrings.of(context).auth.requiredField;
    if (value.trim().length > 100) {
      return AppStrings.of(context).auth.nameTooLong;
    }
    return null;
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
  String? get _passwordError {
    if (!_hasSubmitted) return null;
    final length = _password.text.characters.length;
    if (length < 12 || length > 128) {
      return AppStrings.of(context).auth.passwordLength;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) =>
      BlocConsumer<SignUpFormCubit, SignUpFormState>(
        listener: (_, state) {
          if (state case SignUpFormRejected(
            failure: AuthRejected(
              code: AuthRejectionCode.passwordTooWeak ||
                  AuthRejectionCode.passwordBreached,
            ),
          )) {
            setState(() => _rejectedPassword = _password.text);
          }
        },
        builder: (context, state) {
          final strings = AppStrings.of(context).auth;
          final isSubmitting = state is SignUpFormSubmitting;
          final rejected = state is SignUpFormRejected ? state.failure : null;
          final passwordServerError = switch ((
            rejected,
            _rejectedPassword == _password.text,
          )) {
            (AuthRejected(code: AuthRejectionCode.passwordTooWeak), true) =>
              strings.passwordLength,
            (AuthRejected(code: AuthRejectionCode.passwordBreached), true) =>
              strings.passwordBreached,
            _ => null,
          };
          final isPasswordRejection = switch (rejected) {
            AuthRejected(
              code: AuthRejectionCode.passwordTooWeak ||
                  AuthRejectionCode.passwordBreached,
            ) =>
              true,
            _ => false,
          };
          final generalError = rejected != null && !isPasswordRejection
              ? strings.serverUnreachable
              : null;
          return AutofillGroup(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: AppSpacing.lg,
              children: [
                AppLabeledDivider(label: strings.signUpDivider),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final fields = [
                      AppTextField(
                        label: strings.firstName,
                        placeholder: strings.firstName,
                        controller: _firstName,
                        enabled: !isSubmitting,
                        autofillHints: const [AutofillHints.givenName],
                        textInputAction: TextInputAction.next,
                        errorText: _nameError(_firstName.text),
                        onChanged: (_) {
                          if (_hasSubmitted) setState(() {});
                        },
                      ),
                      AppTextField(
                        label: strings.lastName,
                        placeholder: strings.lastName,
                        controller: _lastName,
                        enabled: !isSubmitting,
                        autofillHints: const [AutofillHints.familyName],
                        textInputAction: TextInputAction.next,
                        errorText: _nameError(_lastName.text),
                        onChanged: (_) {
                          if (_hasSubmitted) setState(() {});
                        },
                      ),
                    ];
                    return constraints.maxWidth < 320
                        ? Column(spacing: AppSpacing.lg, children: fields)
                        : Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            spacing: AppSpacing.lg,
                            children: fields
                                .map((field) => Expanded(child: field))
                                .toList(),
                          );
                  },
                ),
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
                  helperText: strings.passwordHelper,
                  isObscured: true,
                  showObscuredTextTooltip: strings.showPassword,
                  hideObscuredTextTooltip: strings.hidePassword,
                  autofillHints: const [AutofillHints.newPassword],
                  textInputAction: TextInputAction.done,
                  errorText: passwordServerError ?? _passwordError,
                  onChanged: (_) {
                    if (_hasSubmitted) setState(() {});
                  },
                  onSubmitted: (_) => _submit(),
                ),
                _LegalLine(
                  strings: strings,
                  termsUrl: widget.termsUrl,
                  privacyUrl: widget.privacyUrl,
                  enabled: !isSubmitting,
                ),
                if (generalError != null)
                  AppAlert(title: generalError, variant: AppAlertVariant.error),
                AppButton(
                  label: strings.register,
                  onPressed: isSubmitting ? null : _submit,
                  isLoading: isSubmitting,
                  size: AppButtonSize.xxl,
                ),
                AuthSwitchPrompt(
                  prompt: strings.signUpSwitchPrefix,
                  actionLabel: strings.signUpSwitchAction,
                  onPressed: isSubmitting
                      ? null
                      : () => widget.onLogIn(_email.text.trim()),
                ),
              ],
            ),
          );
        },
      );
}

/// Legal agreement copy with two browser links.
class const _LegalLine({
  required final AuthStrings strings,
  required final Uri termsUrl,
  required final Uri privacyUrl,
  required final bool enabled,
}) extends StatelessWidget {
  /// Creates the legal line.
  this;

  @override
  Widget build(BuildContext context) => Wrap(
    alignment: WrapAlignment.center,
    crossAxisAlignment: WrapCrossAlignment.center,
    children: [
      Text('${strings.legalPrefix} '),
      ConstrainedBox(
        constraints: const BoxConstraints(minHeight: AppSizes.controlXxl),
        child: TextButton(
          onPressed: enabled ? () => launchUrl(termsUrl) : null,
          child: Text(strings.termsOfUse),
        ),
      ),
      Text(' ${strings.legalConjunction} '),
      ConstrainedBox(
        constraints: const BoxConstraints(minHeight: AppSizes.controlXxl),
        child: TextButton(
          onPressed: enabled ? () => launchUrl(privacyUrl) : null,
          child: Text(strings.privacyPolicy),
        ),
      ),
    ],
  );
}
