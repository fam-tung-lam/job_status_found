/// Stable backend reasons why an authentication operation was rejected.
enum AuthRejectionCode(
  /// The RFC 9457 `code` value returned by the backend.
  final String wireName,
) {
  /// The submitted email and password did not prove an account.
  invalidCredentials('invalid_credentials'),

  /// The account must verify its email before a session can open.
  emailVerificationRequired('email_verification_required'),

  /// The account cannot currently sign in.
  accountUnavailable('account_unavailable'),

  /// The caller exceeded an operation's rate limit.
  tooManyAttempts('too_many_attempts'),

  /// The submitted new password is outside the policy.
  passwordTooWeak('password_too_weak'),

  /// The submitted password appears in known breach data.
  passwordBreached('password_breached'),

  /// The email-verification proof is invalid or expired.
  verificationCodeInvalid('verification_code_invalid'),

  /// An access token is missing, invalid, or expired.
  accessTokenInvalid('access_token_invalid'),

  /// A refresh token is missing, invalid, or expired.
  refreshTokenInvalid('refresh_token_invalid'),

  /// The session has ended.
  sessionEnded('session_ended'),

  /// The browser refresh request came from a disallowed origin.
  originNotAllowed('origin_not_allowed'),

  /// A future backend rejection is not understood by this app version.
  unknown('unknown');

  /// Decodes a backend [wireName], preserving forward compatibility as
  /// [unknown].
  static AuthRejectionCode fromWireName(String wireName) =>
      AuthRejectionCode.values.firstWhere(
        (code) => code.wireName == wireName,
        orElse: () => AuthRejectionCode.unknown,
      );
}
