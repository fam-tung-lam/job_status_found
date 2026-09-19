import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Token pair returned by a session-creating endpoint.
final class const TokenPairDto({
  /// Short-lived bearer token.
  required final String accessToken,

  /// Rotating refresh token, absent for web.
  required final String? refreshToken,

  /// Access-token lifetime in seconds.
  required final int expiresIn,

  /// Authorization scheme.
  required final JobStatusFoundAuthTokenType tokenType,
}) {
  /// Creates a token pair DTO.
  this;

  /// Decodes the documented API body.
  factory fromJson(Map<String, Object?> json) {
    final accessToken = json['access_token'];
    final refreshToken = json['refresh_token'];
    final expiresIn = json['expires_in'];
    final tokenType = json['token_type'];
    if (accessToken is! String ||
        (refreshToken != null && refreshToken is! String) ||
        expiresIn is! int ||
        tokenType is! String) {
      throw const FormatException('Invalid token pair.');
    }
    final parsedTokenType = JobStatusFoundAuthTokenType.tryFromWireName(
      tokenType,
    );
    if (parsedTokenType == null) {
      throw const FormatException('Invalid token pair.');
    }
    return TokenPairDto(
      accessToken: accessToken,
      refreshToken: refreshToken as String?,
      expiresIn: expiresIn,
      tokenType: parsedTokenType,
    );
  }

  /// Converts to the HTTP package token type.
  JobStatusFoundAuthTokens toAuthTokens() => JobStatusFoundAuthTokens(
    accessToken: accessToken,
    refreshToken: refreshToken,
    expiresIn: expiresIn,
    tokenType: tokenType,
    issuedAt: DateTime.now(),
  );
}
