import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_state.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// Token response returned after successful verification.
const _tokenResponse = <String, Object?>{
  'access_token': 'access-token',
  'refresh_token': 'refresh-token',
  'expires_in': 900,
  'token_type': 'Bearer',
};

/// Profile returned after the verified session opens.
const _currentUserResponse = <String, Object?>{
  'id': 'id',
  'email': 'person@example.com',
  'first_name': 'Pat',
  'last_name': 'Lee',
  'avatar_url': null,
  'locale': null,
  'role': 'user',
  'has_password': true,
  'linked_providers': <Object?>[],
};

/// Builds the complete verification flow above the mocked HTTP boundary.
EmailVerificationCubit _buildCubit(
  MockJobStatusFoundHttpClient httpClient,
  void Function(SignedInUser user) setSignedInUser,
) {
  final repository = ApiAuthRepository(
    AuthApiClient(httpClient),
    httpClient,
    clientKind: ClientKind.android,
  );
  return EmailVerificationCubit(
    ConfirmEmailVerificationUseCase(repository),
    ResendEmailVerificationUseCase(repository),
    setSignedInUser,
  );
}

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  final user = SignedInUser(
    id: 'id',
    email: email,
    firstName: 'Pat',
    lastName: 'Lee',
    avatarUrl: null,
    locale: null,
    role: UserRole.user,
    hasPassword: true,
    linkedProviders: const [],
  );
  late MockJobStatusFoundHttpClient httpClient;
  late SignedInUser? signedInUser;

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
    signedInUser = null;
  });

  blocTest<EmailVerificationCubit, EmailVerificationState>(
    'confirms through the API and publishes the decoded user',
    setUp: () {
      // Given: the API opens a session and returns its current user.
      when(
        () => httpClient.post(
          '/v1/auth/email-verification/confirm',
          body: any(named: 'body'),
        ),
      ).thenAnswer((_) async => _tokenResponse);
      when(() => httpClient.setTokens(any())).thenAnswer((_) async {});
      when(() => httpClient.get('/v1/auth/me'))
          .thenAnswer((_) async => _currentUserResponse);
    },
    build: () => _buildCubit(httpClient, (user) => signedInUser = user),
    act: (cubit) {
      // When: the user submits the verification code.
      return cubit.confirm(
        email: email,
        code: '012345',
        password: 'matching password',
        rememberMe: true,
      );
    },
    expect: () => const [
      // Then: the Cubit reports submission while the session opens.
      EmailVerificationSubmitting(60),
    ],
    verify: (_) {
      // Then: the complete flow publishes the API user.
      expect(signedInUser, user);
    },
  );
}
