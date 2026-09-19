import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/pages/email_verification_page.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';

/// Auth repository observed by verification page tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;

  setUpAll(() {
    registerFallbackValue(email);
  });
  testWidgets('invalid code and missing password prevent confirmation', (
    tester,
  ) async {
    // Given: a verification page reached without ephemeral credentials.
    final repository = _MockAuthRepository();
    final cubit = EmailVerificationCubit(
      ConfirmEmailVerificationUseCase(repository),
      ResendEmailVerificationUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      EmailVerificationPage(
        emailVerificationCubit: cubit,
        email: email,
        initialPassword: '',
        rememberMe: false,
        onUseDifferentEmail: () {},
      ),
    );

    // When: confirmation is attempted without the six digits or password.
    await tester.tap(find.text(const EnAuthStrings().verifyEmail));
    await tester.pump();

    // Then: both required values explain the problem and no request starts.
    expect(
      find.text(const EnAuthStrings().invalidVerificationCode),
      findsOneWidget,
    );
    expect(find.text(const EnAuthStrings().passwordRequired), findsOneWidget);
    verifyNever(
      () => repository.confirmEmailVerification(
        email: any(named: 'email'),
        code: any(named: 'code'),
        password: any(named: 'password'),
        rememberMe: any(named: 'rememberMe'),
      ),
    );
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('resend locks the page and clears the code only after success', (
    tester,
  ) async {
    // Given: the resend interval has elapsed and the API remains in flight.
    final repository = _MockAuthRepository();
    final resend = Completer<void>();
    when(() => repository.resendEmailVerification(email))
        .thenAnswer((_) => resend.future);
    final cubit = EmailVerificationCubit(
      ConfirmEmailVerificationUseCase(repository),
      ResendEmailVerificationUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      EmailVerificationPage(
        emailVerificationCubit: cubit,
        email: email,
        initialPassword: 'matching password',
        rememberMe: false,
        onUseDifferentEmail: () {},
      ),
    );
    await tester.pump(const Duration(seconds: 60));
    final fields = find.byType(TextField);
    await tester.enterText(fields.first, '123456');

    // When: resend starts and a second call is attempted directly.
    await tester.tap(find.text(const EnAuthStrings().resendCode));
    await tester.pump();
    unawaited(cubit.resend(email));

    // Then: the request is single-flight, the code remains, and inputs lock.
    verify(() => repository.resendEmailVerification(email)).called(1);
    expect(tester.widget<TextField>(fields.first).controller?.text, '123456');
    expect(tester.widget<TextField>(fields.first).enabled, isFalse);
    expect(tester.widget<TextField>(fields.at(1)).enabled, isFalse);

    // When: the backend accepts the resend.
    resend.complete();
    await tester.pump();

    // Then: the stale code clears and the page becomes editable again.
    expect(tester.widget<TextField>(fields.first).controller?.text, isEmpty);
    expect(tester.widget<TextField>(fields.first).enabled, isTrue);
    expect(find.text(const EnAuthStrings().verificationResent), findsOneWidget);
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
}
