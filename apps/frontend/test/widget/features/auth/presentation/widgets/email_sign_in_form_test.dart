import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/widgets/email_sign_in_form.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';

/// Auth repository observed by the form test.
final class _MockAuthRepository() extends Mock implements AuthRepository;

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;

  setUpAll(() {
    registerFallbackValue(email);
  });
  testWidgets('first invalid submit shows inline errors and sends no request', (
    tester,
  ) async {
    // Given: an untouched sign-in form.
    final repository = _MockAuthRepository();
    final cubit = SignInFormCubit(
      SignInWithPasswordUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      Scaffold(
        body: SingleChildScrollView(
          child: BlocProvider.value(
            value: cubit,
            child: EmailSignInForm(initialEmail: '', onRegister: (_) {}),
          ),
        ),
      ),
    );

    // When: the person submits without filling either field.
    await tester.tap(find.text(const EnAuthStrings().signIn));
    await tester.pump();

    // Then: both fields explain the problem and no request starts.
    expect(find.text(const EnAuthStrings().invalidEmail), findsOneWidget);
    expect(find.text(const EnAuthStrings().passwordRequired), findsOneWidget);
    verifyNever(
      () => repository.signInWithPassword(
        email: any(named: 'email'),
        password: any(named: 'password'),
        rememberMe: any(named: 'rememberMe'),
      ),
    );
    await cubit.close();
  });

  testWidgets('web remember choice starts clear and submits false', (
    tester,
  ) async {
    // Given: the web-only persistence choice has not been selected.
    final repository = _MockAuthRepository();
    when(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: false,
      ),
    ).thenThrow(const AuthRejected(AuthRejectionCode.invalidCredentials));
    final cubit = SignInFormCubit(
      SignInWithPasswordUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      Scaffold(
        body: BlocProvider.value(
          value: cubit,
          child: EmailSignInForm(
            initialEmail: '',
            onRegister: (_) {},
            showRememberDevice: true,
          ),
        ),
      ),
    );
    final checkbox = tester.widget<Checkbox>(find.byType(Checkbox));
    expect(checkbox.value, isFalse);
    final fields = find.byType(TextField);
    await tester.enterText(fields.at(0), 'person@example.com');
    await tester.enterText(fields.at(1), 'password');

    // When: sign-in is submitted without changing persistence.
    await tester.tap(find.text(const EnAuthStrings().signIn));
    await tester.pump();

    // Then: the API receives the unchecked value.
    verify(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: false,
      ),
    ).called(1);
    await cubit.close();
  });

  testWidgets('non-web sign-in hides persistence choice and submits true', (
    tester,
  ) async {
    // Given: a mobile sign-in form with its persistence behavior fixed on.
    final repository = _MockAuthRepository();
    when(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: true,
      ),
    ).thenThrow(const AuthRejected(AuthRejectionCode.invalidCredentials));
    final cubit = SignInFormCubit(
      SignInWithPasswordUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      Scaffold(
        body: BlocProvider.value(
          value: cubit,
          child: EmailSignInForm(
            initialEmail: '',
            onRegister: (_) {},
            showRememberDevice: false,
          ),
        ),
      ),
    );
    expect(find.byType(Checkbox), findsNothing);
    final fields = find.byType(TextField);
    await tester.enterText(fields.at(0), 'person@example.com');
    await tester.enterText(fields.at(1), 'password');

    // When: mobile sign-in is submitted.
    await tester.tap(find.text(const EnAuthStrings().signIn));
    await tester.pump();

    // Then: the API receives the required persistent-session value.
    verify(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: true,
      ),
    ).called(1);
    await cubit.close();
  });

  testWidgets('selected web persistence is sent and the form locks in flight', (
    tester,
  ) async {
    // Given: a valid web form whose sign-in request remains in flight.
    final user = SignedInUser(
      id: 'id',
      email: email,
      firstName: null,
      lastName: null,
      avatarUrl: null,
      locale: null,
      role: UserRole.user,
      hasPassword: true,
      linkedProviders: const [],
    );
    final repository = _MockAuthRepository();
    final response = Completer<SignedInUser>();
    when(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: true,
      ),
    ).thenAnswer((_) => response.future);
    final cubit = SignInFormCubit(
      SignInWithPasswordUseCase(repository),
      (_) {},
    );
    await tester.pumpApp(
      Scaffold(
        body: BlocProvider.value(
          value: cubit,
          child: EmailSignInForm(
            initialEmail: '',
            onRegister: (_) {},
            showRememberDevice: true,
          ),
        ),
      ),
    );
    final fields = find.byType(TextField);
    await tester.enterText(fields.at(0), 'person@example.com');
    await tester.enterText(fields.at(1), 'password');
    await tester.tap(find.byType(Checkbox));

    // When: the selected persistent sign-in starts.
    await tester.tap(find.text(const EnAuthStrings().signIn));
    await tester.pump();

    // Then: the selected value is sent and every form control is disabled.
    verify(
      () => repository.signInWithPassword(
        email: email,
        password: 'password',
        rememberMe: true,
      ),
    ).called(1);
    expect(tester.widget<TextField>(fields.at(0)).enabled, isFalse);
    expect(tester.widget<TextField>(fields.at(1)).enabled, isFalse);
    expect(tester.widget<Checkbox>(find.byType(Checkbox)).onChanged, isNull);
    expect(
      tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
      isNull,
    );
    expect(
      tester
          .widgetList<TextButton>(find.byType(TextButton))
          .every((button) => button.onPressed == null),
      isTrue,
    );
    response.complete(user);
    await tester.pump();
    await cubit.close();
  });

  final rejectionScenarios =
      <({String name, AuthFailure failure, String expectedMessage})>[
        (
          name: 'invalid credentials',
          failure: const AuthRejected(AuthRejectionCode.invalidCredentials),
          expectedMessage: const EnAuthStrings().invalidCredentials,
        ),
        (
          name: 'unavailable account',
          failure: const AuthRejected(AuthRejectionCode.accountUnavailable),
          expectedMessage: const EnAuthStrings().accountUnavailable,
        ),
        (
          name: 'throttling',
          failure: const AuthRejected(
            AuthRejectionCode.tooManyAttempts,
            retryAfterSeconds: 125,
          ),
          expectedMessage: const EnAuthStrings().tooManyAttempts(3),
        ),
        (
          name: 'server connectivity',
          failure: const AuthServerUnreachable(),
          expectedMessage: const EnAuthStrings().serverUnreachable,
        ),
      ];
  for (final scenario in rejectionScenarios) {
    testWidgets('shows ${scenario.name} failure and clears the password', (
      tester,
    ) async {
      // Given: a valid form rejected for one stable reason.
      final repository = _MockAuthRepository();
      when(
        () => repository.signInWithPassword(
          email: email,
          password: 'password',
          rememberMe: false,
        ),
      ).thenThrow(scenario.failure);
      final cubit = SignInFormCubit(
        SignInWithPasswordUseCase(repository),
        (_) {},
      );
      await tester.pumpApp(
        Scaffold(
          body: BlocProvider.value(
            value: cubit,
            child: EmailSignInForm(
              initialEmail: '',
              onRegister: (_) {},
              showRememberDevice: true,
            ),
          ),
        ),
      );
      final fields = find.byType(TextField);
      await tester.enterText(fields.at(0), 'person@example.com');
      await tester.enterText(fields.at(1), 'password');

      // When: sign-in receives the rejection.
      await tester.tap(find.text(const EnAuthStrings().signIn));
      await tester.pump();

      // Then: stable localized copy appears and the password is removed.
      expect(find.text(scenario.expectedMessage), findsOneWidget);
      expect(tester.widget<TextField>(fields.at(1)).controller?.text, isEmpty);
      await cubit.close();
    });
  }
}
