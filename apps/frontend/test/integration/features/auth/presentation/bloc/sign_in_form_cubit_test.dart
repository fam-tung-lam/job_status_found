import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_state.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// URL reported by failed sign-in requests.
final Uri _signInUrl = Uri.parse('https://api.example.com/v1/auth/sign-in');

/// Builds the complete sign-in flow above the mocked HTTP boundary.
SignInFormCubit _buildCubit(MockJobStatusFoundHttpClient httpClient) {
  final repository = ApiAuthRepository(
    AuthApiClient(httpClient),
    httpClient,
    clientKind: ClientKind.android,
  );
  return SignInFormCubit(SignInWithPasswordUseCase(repository), (_) {});
}

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  late MockJobStatusFoundHttpClient httpClient;

  setUp(() {
    httpClient = MockJobStatusFoundHttpClient();
  });

  blocTest<SignInFormCubit, SignInFormState>(
    'preserves credentials when the API requires email verification',
    setUp: () {
      // Given: the lowest HTTP boundary returns the stable verification code.
      when(() => httpClient.post('/v1/auth/sign-in', body: any(named: 'body')))
          .thenThrow(
            JobStatusFoundHttpClientBadResponse(
              _signInUrl,
              statusCode: 403,
              body: const {'code': 'email_verification_required'},
              code: 'email_verification_required',
              retryAfterSeconds: null,
            ),
          );
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) {
      // When: the user submits credentials with remembered persistence.
      return cubit.submit(email: email, password: 'secret', rememberMe: true);
    },
    expect: () => [
      // Then: the Cubit carries the original values into verification.
      const SignInFormSubmitting(),
      SignInFormEmailVerificationRequired(
        email,
        'secret',
        SessionPersistence.remembered,
      ),
    ],
  );

  blocTest<SignInFormCubit, SignInFormState>(
    'exposes the API invalid-credentials rejection',
    setUp: () {
      // Given: the lowest HTTP boundary rejects the credentials.
      when(() => httpClient.post('/v1/auth/sign-in', body: any(named: 'body')))
          .thenThrow(
            JobStatusFoundHttpClientBadResponse(
              _signInUrl,
              statusCode: 401,
              body: const {'code': 'invalid_credentials'},
              code: 'invalid_credentials',
              retryAfterSeconds: null,
            ),
          );
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) {
      // When: the user submits invalid credentials.
      return cubit.submit(email: email, password: 'wrong', rememberMe: false);
    },
    expect: () => [
      // Then: the Cubit exposes the stable domain rejection.
      const SignInFormSubmitting(),
      isA<SignInFormRejected>().having(
        (state) => state.failure,
        'failure',
        isA<AuthRejectedFailure>().having(
          (failure) => failure.code,
          'code',
          AuthRejectionCode.invalidCredentials,
        ),
      ),
    ],
  );
}
