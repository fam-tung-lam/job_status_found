import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/widgets/email_sign_up_form.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';

/// Auth repository observed by sign-up form tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;

  setUpAll(() {
    registerFallbackValue(email);
  });
  testWidgets('invalid fields prevent registration', (tester) async {
    // Given: an untouched sign-up form.
    final repository = _MockAuthRepository();
    final cubit = SignUpFormCubit(SignUpWithPasswordUseCase(repository));
    await tester.pumpApp(
      Scaffold(
        body: SingleChildScrollView(
          child: BlocProvider.value(
            value: cubit,
            child: EmailSignUpForm(
              initialEmail: '',
              termsUrl: Uri.parse('https://example.com/terms'),
              privacyUrl: Uri.parse('https://example.com/privacy'),
              onLogIn: (_) {},
            ),
          ),
        ),
      ),
    );

    // When: registration is attempted without any values.
    await tester.tap(find.text(const EnAuthStrings().register));
    await tester.pump();

    // Then: every field explains its boundary and no request starts.
    expect(find.text(const EnAuthStrings().requiredField), findsNWidgets(2));
    expect(find.text(const EnAuthStrings().invalidEmail), findsOneWidget);
    expect(find.text(const EnAuthStrings().passwordLength), findsOneWidget);
    verifyNever(
      () => repository.signUpWithPassword(
        firstName: any(named: 'firstName'),
        lastName: any(named: 'lastName'),
        email: any(named: 'email'),
        password: any(named: 'password'),
      ),
    );
    await cubit.close();
  });

  testWidgets('a breached-password rejection clears after password editing', (
    tester,
  ) async {
    // Given: valid values whose password is rejected by the API.
    final repository = _MockAuthRepository();
    when(
      () => repository.signUpWithPassword(
        firstName: 'Pat',
        lastName: 'Lee',
        email: email,
        password: 'breached password',
      ),
    ).thenThrow(const AuthRejectedFailure(AuthRejectionCode.passwordBreached));
    final cubit = SignUpFormCubit(SignUpWithPasswordUseCase(repository));
    await tester.pumpApp(
      Scaffold(
        body: SingleChildScrollView(
          child: BlocProvider.value(
            value: cubit,
            child: EmailSignUpForm(
              initialEmail: '',
              termsUrl: Uri.parse('https://example.com/terms'),
              privacyUrl: Uri.parse('https://example.com/privacy'),
              onLogIn: (_) {},
            ),
          ),
        ),
      ),
    );
    final fields = find.byType(TextField);
    await tester.enterText(fields.at(0), 'Pat');
    await tester.enterText(fields.at(1), 'Lee');
    await tester.enterText(fields.at(2), 'person@example.com');
    await tester.enterText(fields.at(3), 'breached password');
    await tester.tap(find.text(const EnAuthStrings().register));
    await tester.pump();
    expect(find.text(const EnAuthStrings().passwordBreached), findsOneWidget);

    // When: the person changes the rejected password.
    await tester.enterText(fields.at(3), 'different secure password');
    await tester.pump();

    // Then: the stale server validation no longer describes the new value.
    expect(find.text(const EnAuthStrings().passwordBreached), findsNothing);
    await cubit.close();
  });
}
