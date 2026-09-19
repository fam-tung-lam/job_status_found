import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Token storage backed by the platform's encrypted storage implementation.
final class const SecureJobStatusFoundTokenStorage(
  /// Reads and writes encrypted platform storage.
  final FlutterSecureStorage _secureStorage,
) implements JobStatusFoundTokenStorage {
  /// Creates secure token storage.
  this;

  /// Key holding the one serialized token set.
  static const _storageKey = 'job_status_found_auth_tokens';

  @override
  Future<void> delete() => _secureStorage.delete(key: _storageKey);

  @override
  Future<JobStatusFoundAuthTokens?> read() async {
    final encodedTokens = await _secureStorage.read(key: _storageKey);
    if (encodedTokens == null) return null;
    try {
      final json = jsonDecode(encodedTokens);
      if (json is! Map<String, Object?>) return null;
      final accessToken = json['access_token'];
      final refreshToken = json['refresh_token'];
      final expiresAtText = json['expires_at'];
      final tokenTypeText = json['token_type'];
      final expiresAt = expiresAtText is String
          ? DateTime.tryParse(expiresAtText)
          : null;
      final tokenType = tokenTypeText is String
          ? JobStatusFoundAuthTokenType.tryFromWireName(tokenTypeText)
          : null;
      if (accessToken is! String ||
          (refreshToken != null && refreshToken is! String) ||
          expiresAt == null ||
          tokenType == null) {
        return null;
      }
      final issuedAt = DateTime.now();
      return JobStatusFoundAuthTokens(
        accessToken: accessToken,
        refreshToken: refreshToken as String?,
        expiresIn: expiresAt.difference(issuedAt).inSeconds,
        tokenType: tokenType,
        issuedAt: issuedAt,
      );
    } on FormatException {
      return null;
    }
  }

  @override
  Future<void> write(JobStatusFoundAuthTokens tokens) => _secureStorage.write(
    key: _storageKey,
    value: jsonEncode({
      'access_token': tokens.accessToken,
      'refresh_token': tokens.refreshToken,
      'expires_at': tokens.issuedAt
          .add(Duration(seconds: tokens.expiresIn))
          .toIso8601String(),
      'token_type': tokens.tokenType.wireName,
    }),
  );
}
