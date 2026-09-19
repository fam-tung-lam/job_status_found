/// User-visible authentication copy.
sealed class const AuthStrings() {
  /// Creates auth strings.
  this;

  /// Sign-in page headline.
  String get signInHeadline;

  /// Sign-up page headline.
  String get signUpHeadline;

  /// Shared marketing subtitle.
  String get subtitle;

  /// Sign-in email divider.
  String get signInDivider;

  /// Sign-up email divider.
  String get signUpDivider;

  /// Given-name label.
  String get firstName;

  /// Family-name label.
  String get lastName;

  /// Email label and placeholder.
  String get emailAddress;

  /// Password label and placeholder.
  String get password;

  /// Action that reveals a hidden password.
  String get showPassword;

  /// Action that hides a visible password.
  String get hidePassword;

  /// New-password guidance.
  String get passwordHelper;

  /// Persistent-session checkbox label.
  String get rememberDevice;

  /// Persistent-session explanation.
  String get rememberDeviceHelp;

  /// Sign-in action.
  String get signIn;

  /// Registration action.
  String get register;

  /// Sign-in switch prompt.
  String get signInSwitchPrefix;

  /// Sign-in switch action.
  String get signInSwitchAction;

  /// Sign-up switch prompt.
  String get signUpSwitchPrefix;

  /// Sign-up switch action.
  String get signUpSwitchAction;

  /// Legal sentence prefix.
  String get legalPrefix;

  /// Terms link label.
  String get termsOfUse;

  /// Conjunction between legal links.
  String get legalConjunction;

  /// Privacy link label.
  String get privacyPolicy;

  /// Required-field validation.
  String get requiredField;

  /// Name length validation.
  String get nameTooLong;

  /// Email syntax validation.
  String get invalidEmail;

  /// Empty-password validation.
  String get passwordRequired;

  /// New-password length validation.
  String get passwordLength;

  /// Invalid credential rejection.
  String get invalidCredentials;

  /// Unavailable-account rejection.
  String get accountUnavailable;

  /// Throttle rejection with retry delay.
  String tooManyAttempts(int minutes);

  /// Connectivity and server failure.
  String get serverUnreachable;

  /// Breached-password rejection.
  String get passwordBreached;

  /// Verification page headline.
  String get checkEmailHeadline;

  /// Verification instructions naming [email].
  String verificationExplanation(String email);

  /// Verification-code label.
  String get verificationCode;

  /// Verification-code syntax validation.
  String get invalidVerificationCode;

  /// Verification submit action.
  String get verifyEmail;

  /// Enabled resend action.
  String get resendCode;

  /// Disabled resend action with countdown.
  String resendCodeIn(int seconds);

  /// Return-to-sign-in action.
  String get useDifferentEmail;

  /// Invalid code or password rejection.
  String get verificationInvalid;

  /// Generic resend confirmation.
  String get verificationResent;
}

/// English authentication copy.
final class const EnAuthStrings() extends AuthStrings {
  /// Creates English auth strings.
  this;
  @override
  String get signInHeadline => 'Apply to jobs in 1-click';
  @override
  String get signUpHeadline => 'Apply to jobs in 1-click';
  @override
  String get subtitle =>
      'Power your entire job search, with our recruiter-approved AI.';
  @override
  String get signInDivider => 'Or login with your email';
  @override
  String get signUpDivider => 'Or create an account with your email';
  @override
  String get firstName => 'First Name';
  @override
  String get lastName => 'Last Name';
  @override
  String get emailAddress => 'Email Address';
  @override
  String get password => 'Password';
  @override
  String get showPassword => 'Show password';
  @override
  String get hidePassword => 'Hide password';
  @override
  String get passwordHelper => 'At least 12 characters';
  @override
  String get rememberDevice => 'Remember this device';
  @override
  String get rememberDeviceHelp =>
      'Stay signed in on this device for 30 days. '
      'Do not use on a shared computer.';
  @override
  String get signIn => 'Sign in';
  @override
  String get register => 'Register';
  @override
  String get signInSwitchPrefix => "Don't have an account?";
  @override
  String get signInSwitchAction => 'Register.';
  @override
  String get signUpSwitchPrefix => 'Already have an account?';
  @override
  String get signUpSwitchAction => 'Log in.';
  @override
  String get legalPrefix => 'By signing up you agree to our';
  @override
  String get termsOfUse => 'Terms of Use';
  @override
  String get legalConjunction => 'and';
  @override
  String get privacyPolicy => 'Privacy Policy.';
  @override
  String get requiredField => 'This field is required.';
  @override
  String get nameTooLong => 'Use no more than 100 characters.';
  @override
  String get invalidEmail => 'Enter a valid email address.';
  @override
  String get passwordRequired => 'Enter your password.';
  @override
  String get passwordLength => 'Use at least 12 characters.';
  @override
  String get invalidCredentials => 'Email or password is incorrect.';
  @override
  String get accountUnavailable =>
      'This account is not available. Contact support.';
  @override
  String tooManyAttempts(int minutes) =>
      'Too many attempts. Try again in $minutes minutes.';
  @override
  String get serverUnreachable =>
      'We could not reach the server. Check your connection and try again.';
  @override
  String get passwordBreached =>
      'This password appears in known data breaches. Choose another.';
  @override
  String get checkEmailHeadline => 'Check your email';
  @override
  String verificationExplanation(String email) =>
      'Enter the 6-digit code sent to $email and the password used for this '
      'sign-up.';
  @override
  String get verificationCode => '6-digit code';
  @override
  String get invalidVerificationCode => 'Enter the 6-digit code.';
  @override
  String get verifyEmail => 'Verify email';
  @override
  String get resendCode => 'Resend code';
  @override
  String resendCodeIn(int seconds) => 'Resend code in $seconds s';
  @override
  String get useDifferentEmail => 'Use a different email';
  @override
  String get verificationInvalid =>
      'The code or password is incorrect, expired, or no longer works. '
      'Check both, or request a new code.';
  @override
  String get verificationResent => 'Check your inbox for a new code.';
}
