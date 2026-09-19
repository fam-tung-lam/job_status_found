import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/secure_job_status_found_token_storage.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

/// Secure-storage plugin boundary controlled by persistence tests.
final class _MockFlutterSecureStorage()
    extends Mock
    implements FlutterSecureStorage {
  /// Creates the mock plugin boundary.
  this;
}

void main() {
  test('mobile tokens survive a storage adapter restart', () async {
    // Given: one mocked Keychain or Keystore boundary shared across restarts.
    final secureStorage = _MockFlutterSecureStorage();
    String? encryptedPayload;
    when(
      () => secureStorage.write(
        key: any(named: 'key'),
        value: any(named: 'value'),
      ),
    ).thenAnswer((invocation) async {
      encryptedPayload = invocation.namedArguments[#value]! as String;
    });
    when(() => secureStorage.read(key: any(named: 'key')))
        .thenAnswer((_) async => encryptedPayload);
    final firstProcess = SecureJobStatusFoundTokenStorage(secureStorage);
    final issuedAt = DateTime.now();

    // When: one process stores tokens and a new adapter reads them later.
    await firstProcess.write(
      JobStatusFoundAuthTokens(
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        expiresIn: 3600,
        tokenType: JobStatusFoundAuthTokenType.bearer,
        issuedAt: issuedAt,
      ),
    );
    final restartedProcess = SecureJobStatusFoundTokenStorage(secureStorage);
    final restoredTokens = await restartedProcess.read();

    // Then: both mobile tokens and expiry metadata survive the restart.
    expect(restoredTokens?.accessToken, 'access-token');
    expect(restoredTokens?.refreshToken, 'refresh-token');
    expect(restoredTokens?.tokenType, JobStatusFoundAuthTokenType.bearer);
    expect(restoredTokens?.expiresIn, inInclusiveRange(3598, 3600));
  });

  test('web access tokens survive without a stored refresh token', () async {
    // Given: secure storage preserves one serialized browser token set.
    final secureStorage = _MockFlutterSecureStorage();
    String? encryptedPayload;
    when(
      () => secureStorage.write(
        key: any(named: 'key'),
        value: any(named: 'value'),
      ),
    ).thenAnswer((invocation) async {
      encryptedPayload = invocation.namedArguments[#value]! as String;
    });
    when(() => secureStorage.read(key: any(named: 'key')))
        .thenAnswer((_) async => encryptedPayload);
    final storage = SecureJobStatusFoundTokenStorage(secureStorage);

    // When: a cookie-backed web session stores and reads its access token.
    await storage.write(
      JobStatusFoundAuthTokens(
        accessToken: 'access-token',
        refreshToken: null,
        expiresIn: 3600,
        tokenType: JobStatusFoundAuthTokenType.bearer,
        issuedAt: DateTime.now(),
      ),
    );
    final restoredTokens = await storage.read();

    // Then: absence of the HTTP-only cookie value does not invalidate the
    // access token.
    expect(restoredTokens?.accessToken, 'access-token');
    expect(restoredTokens?.refreshToken, isNull);
  });
}
