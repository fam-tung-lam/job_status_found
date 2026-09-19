import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_state.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// Builds the complete sign-up flow above the mocked HTTP boundary.
SignUpFormCubit _buildCubit(MockJobStatusFoundHttpClient httpClient) {
  final repository = ApiAuthRepository(
    AuthApiClient(httpClient),
    httpClient,
    clientKind: ClientKind.android,
  );
  return SignUpFormCubit(SignUpWithPasswordUseCase(repository));
}

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  late MockJobStatusFoundHttpClient httpClient;

  setUp(() {
    httpClient = MockJobStatusFoundHttpClient();
  });

  blocTest<SignUpFormCubit, SignUpFormState>(
    'submits to the API then carries credentials to verification',
    setUp: () {
      // Given: the lowest HTTP boundary accepts the sign-up request.
      when(() => httpClient.post('/v1/auth/sign-up', body: any(named: 'body')))
          .thenAnswer((_) async => null);
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) {
      // When: the user submits the sign-up form.
      return cubit.submit(
        firstName: 'Pat',
        lastName: 'Lee',
        email: email,
        password: 'secure password',
      );
    },
    expect: () => [
      // Then: the Cubit advances with the accepted credentials.
      const SignUpFormSubmitting(),
      SignUpFormVerificationRequired(email, 'secure password'),
    ],
  );
}
