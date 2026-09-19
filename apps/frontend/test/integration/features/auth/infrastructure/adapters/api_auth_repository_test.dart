import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  late MockJobStatusFoundHttpClient httpClient;
  late ApiAuthRepository repository;

  setUpAll(() {
    registerFallbackValue(
      JobStatusFoundAuthTokens(
        accessToken: 'fallback-access-token',
        refreshToken: 'fallback-refresh-token',
        expiresIn: 1,
        tokenType: JobStatusFoundAuthTokenType.bearer,
        issuedAt: DateTime.fromMillisecondsSinceEpoch(0),
      ),
    );
  });

  setUp(() {
    httpClient = MockJobStatusFoundHttpClient();
    repository = ApiAuthRepository(
      AuthApiClient(httpClient),
      httpClient,
      clientKind: ClientKind.android,
    );
  });

  test('maps a backend rejection to the typed auth failure', () async {
    // Given: the API rejects the submitted credentials with a stable code.
    when(() => httpClient.post('/v1/auth/sign-in', body: any(named: 'body')))
        .thenThrow(
          JobStatusFoundHttpClientBadResponse(
            Uri.parse('https://api.example.com/v1/auth/sign-in'),
            statusCode: 401,
            body: const {'code': 'invalid_credentials'},
            code: 'invalid_credentials',
            retryAfterSeconds: null,
          ),
        );

    // When: the repository signs in.
    final signIn = repository.signInWithPassword(
      email: email,
      password: 'wrong password',
      rememberMe: true,
    );

    // Then: no HTTP-package exception crosses the repository boundary.
    await expectLater(
      signIn,
      throwsA(
        isA<AuthRejected>().having(
          (failure) => failure.code,
          'code',
          AuthRejectionCode.invalidCredentials,
        ),
      ),
    );
  });

  test('maps token-storage exceptions to an auth-domain failure', () async {
    // Given: the API opens a session but persistence fails.
    when(() => httpClient.post('/v1/auth/sign-in', body: any(named: 'body')))
        .thenAnswer(
          (_) async => {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token',
            'expires_in': 900,
            'token_type': 'Bearer',
          },
        );
    when(() => httpClient.setTokens(any())).thenThrow(Exception('storage'));

    // When: the repository stores the session.
    final signIn = repository.signInWithPassword(
      email: email,
      password: 'correct password',
      rememberMe: true,
    );

    // Then: storage implementation details do not cross into application code.
    await expectLater(signIn, throwsA(isA<AuthServerUnreachable>()));
  });

  test('maps credential-observation exceptions to an auth failure', () async {
    // Given: credential storage fails while the client observes its status.
    when(() => httpClient.authenticationStatus).thenAnswer(
      (_) => Stream<JobStatusFoundAuthenticationStatus>.error(
        Exception('storage'),
      ),
    );

    // When: the repository observes authentication status.
    final statuses = repository.watchAuthenticationStatus();

    // Then: the stream exposes only the auth domain failure.
    await expectLater(statuses, emitsError(isA<AuthServerUnreachable>()));
  });

  test('clears partial tokens and maps an invalid profile response', () async {
    // Given: tokens are stored but the current-user response violates its
    // schema.
    when(() => httpClient.post('/v1/auth/sign-in', body: any(named: 'body')))
        .thenAnswer(
          (_) async => {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token',
            'expires_in': 900,
            'token_type': 'Bearer',
          },
        );
    when(() => httpClient.setTokens(any())).thenAnswer((_) async {});
    when(() => httpClient.get('/v1/auth/me')).thenAnswer((_) async => []);
    when(httpClient.clearTokens).thenAnswer((_) async {});

    // When: the repository resolves the signed-in account.
    final signIn = repository.signInWithPassword(
      email: email,
      password: 'correct password',
      rememberMe: true,
    );

    // Then: the repository removes the unusable session and exposes one
    // domain failure.
    await expectLater(signIn, throwsA(isA<AuthServerUnreachable>()));
    verify(httpClient.clearTokens).called(1);
  });
}
