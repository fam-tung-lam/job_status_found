import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/pages/sign_up_page.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';

/// Lowest external API boundary controlled by the registration flow test.
final class _MockJobStatusFoundHttpClient()
    extends Mock
    implements JobStatusFoundHttpClient {
  /// Creates the mock HTTP client.
  this;
}

void main() {
  testWidgets('registration reaches verification through real layers', (
    tester,
  ) async {
    // Given: the API accepts a registration submitted through real app layers.
    final httpClient = _MockJobStatusFoundHttpClient();
    when(() => httpClient.post('/v1/auth/sign-up', body: any(named: 'body')))
        .thenAnswer((_) async => null);
    final repository = ApiAuthRepository(
      AuthApiClient(httpClient),
      httpClient,
      clientKind: ClientKind.web,
    );
    String? verificationEmail;
    String? verificationPassword;
    await tester.pumpApp(
      SignUpPage(
        signUpFormCubit: SignUpFormCubit(SignUpWithPasswordUseCase(repository)),
        initialEmail: '',
        termsUrl: Uri.parse('https://example.com/terms'),
        privacyUrl: Uri.parse('https://example.com/privacy'),
        onLogIn: (_) {},
        onVerificationRequired: (email, password) {
          verificationEmail = email;
          verificationPassword = password;
        },
      ),
    );
    final fields = find.byType(TextField);
    await tester.enterText(fields.at(0), 'Pat');
    await tester.enterText(fields.at(1), 'Lee');
    await tester.enterText(fields.at(2), 'person@example.com');
    await tester.enterText(fields.at(3), 'a secure password');

    // When: the person submits the valid page.
    final register = find.text(const EnAuthStrings().register);
    await tester.ensureVisible(register);
    await tester.tap(register);
    await tester.pump();

    // Then: the wire request is correct and ephemeral credentials move on.
    verify(
      () => httpClient.post(
        '/v1/auth/sign-up',
        body: {
          'first_name': 'Pat',
          'last_name': 'Lee',
          'email': 'person@example.com',
          'password': 'a secure password',
        },
      ),
    ).called(1);
    expect(verificationEmail, 'person@example.com');
    expect(verificationPassword, 'a secure password');
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
}
