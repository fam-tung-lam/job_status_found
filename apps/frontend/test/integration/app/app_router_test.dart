import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:job_status_found/app/app.dart';
import 'package:job_status_found/app/app_router.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/restore_session_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/watch_authentication_status_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:mocktail/mocktail.dart';

/// Auth boundary controlled by router tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

/// Health boundary required to build the signed-in home page.
final class _MockHealthRepository() extends Mock implements HealthRepository;

void main() {
  late GetIt getIt;
  late _MockAuthRepository authRepository;
  late _MockHealthRepository healthRepository;
  late StreamController<AuthenticationStatus> authStatus;
  late AuthSessionCubit session;
  late GoRouter router;

  setUp(() {
    getIt = GetIt.asNewInstance();
    authRepository = _MockAuthRepository();
    healthRepository = _MockHealthRepository();
    when(() => healthRepository.checkBackendHealth()).thenAnswer((_) async {});
    authStatus = StreamController<AuthenticationStatus>.broadcast();
    when(authRepository.watchAuthenticationStatus)
        .thenAnswer((_) => authStatus.stream);
    session = AuthSessionCubit(
      RestoreSessionUseCase(authRepository),
      WatchAuthenticationStatusUseCase(authRepository),
    );
    getIt
      ..registerSingleton(AppSettings.fromApiBaseUrl('http://localhost:8000'))
      ..registerFactory(
        () => SignInFormCubit(
          SignInWithPasswordUseCase(authRepository),
          session.setSignedInUser,
        ),
      )
      ..registerFactory(
        () => EmailVerificationCubit(
          ConfirmEmailVerificationUseCase(authRepository),
          ResendEmailVerificationUseCase(authRepository),
          session.setSignedInUser,
        ),
      )
      ..registerFactory(
        () => SignUpFormCubit(SignUpWithPasswordUseCase(authRepository)),
      )
      ..registerFactory(() => CheckHealthUseCase(healthRepository));
    router = createAppRouter(getIt, session);
  });

  tearDown(() async {
    router.dispose();
    await session.close();
    await authStatus.close();
    await getIt.reset();
  });

  testWidgets(
    'shows restoration, guards home, and rejects auth pages after sign-in',
    (tester) async {
      // Given: startup session restoration has not answered yet.
      when(() => authRepository.restoreSession()).thenAnswer((_) async => null);
      await tester.pumpWidget(App(router: router));
      await tester.pump();

      // Then: restoration has its own route instead of flashing sign-in.
      expect(
        router.routeInformationProvider.value.uri.path,
        '/restoring-session',
      );

      // When: restoration confirms there is no session.
      await session.restoreSession();
      await tester.pumpAndSettle();

      // Then: the protected home route becomes sign-in.
      expect(router.routeInformationProvider.value.uri.path, SignInRoute.path);

      // When: verification is opened without an email to identify the flow.
      router.go(EmailVerificationRoute.path);
      await tester.pumpAndSettle();

      // Then: the unusable verification route returns to sign-in.
      expect(router.routeInformationProvider.value.uri.path, SignInRoute.path);

      // When: a session opens and the person explicitly requests sign-in again.
      session.setSignedInUser(
        SignedInUser(
          id: 'id',
          email: EmailAddress.tryParse('person@example.com')!,
          firstName: null,
          lastName: null,
          avatarUrl: null,
          locale: null,
          role: UserRole.user,
          hasPassword: true,
          linkedProviders: const [],
        ),
      );
      await tester.pumpAndSettle();
      router.go(SignInRoute.path);
      await tester.pumpAndSettle();

      // Then: signed-in auth pages redirect back home.
      expect(router.routeInformationProvider.value.uri.path, HomeRoute.path);
    },
  );

  testWidgets('preserves a direct verification route through restoration', (
    tester,
  ) async {
    // Given: a direct verification URL while session status is unresolved.
    when(() => authRepository.restoreSession()).thenAnswer((_) async => null);
    await tester.pumpWidget(App(router: router));
    router.go(EmailVerificationRoute.location('person@example.com'));
    await tester.pump();
    await tester.pump();
    expect(
      router.routeInformationProvider.value.uri.path,
      '/restoring-session',
    );

    // When: restoration proves there is no current session.
    await session.restoreSession();
    await tester.pumpAndSettle();

    // Then: verification keeps its email and requests password re-entry.
    expect(
      router.routeInformationProvider.value.uri,
      Uri.parse('/verify-email?email=person%40example.com'),
    );
    expect(find.textContaining('person@example.com'), findsOneWidget);
  });

  testWidgets('preserves direct sign-up through restoration', (tester) async {
    // Given: a direct registration URL while session status is unresolved.
    when(() => authRepository.restoreSession()).thenAnswer((_) async => null);
    await tester.pumpWidget(App(router: router));
    router.go(SignUpRoute.location('person@example.com'));
    await tester.pump();
    await tester.pump();

    // When: restoration proves there is no current session.
    await session.restoreSession();
    await tester.pumpAndSettle();

    // Then: the registration route and entered email intent survive.
    expect(
      router.routeInformationProvider.value.uri,
      Uri.parse('/sign-up?email=person%40example.com'),
    );
    expect(find.text('person@example.com'), findsOneWidget);
  });
}
