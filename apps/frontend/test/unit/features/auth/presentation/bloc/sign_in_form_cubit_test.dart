import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_state.dart';
import 'package:mocktail/mocktail.dart';

/// Auth repository controlled by each test.
final class _MockAuthRepository() extends Mock implements AuthRepository;

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  late _MockAuthRepository repository;

  setUp(() {
    repository = _MockAuthRepository();
  });

  blocTest<SignInFormCubit, SignInFormState>(
    'preserves credentials and persistence when email verification is required',
    setUp: () {
      when(
        () => repository.signInWithPassword(
          email: email,
          password: 'secret',
          rememberMe: true,
        ),
      ).thenThrow(
        const AuthRejected(AuthRejectionCode.emailVerificationRequired),
      );
    },
    build: () => SignInFormCubit(SignInWithPasswordUseCase(repository), (_) {}),
    act: (cubit) =>
        cubit.submit(email: email, password: 'secret', rememberMe: true),
    expect: () => [
      const SignInFormSubmitting(),
      SignInFormEmailVerificationRequired(
        email,
        'secret',
        SessionPersistence.remembered,
      ),
    ],
  );

  blocTest<SignInFormCubit, SignInFormState>(
    'exposes the stable rejection for the form message',
    setUp: () {
      when(
        () => repository.signInWithPassword(
          email: email,
          password: 'wrong',
          rememberMe: false,
        ),
      ).thenThrow(const AuthRejected(AuthRejectionCode.invalidCredentials));
    },
    build: () => SignInFormCubit(SignInWithPasswordUseCase(repository), (_) {}),
    act: (cubit) =>
        cubit.submit(email: email, password: 'wrong', rememberMe: false),
    expect: () => const [
      SignInFormSubmitting(),
      SignInFormRejected(AuthRejected(AuthRejectionCode.invalidCredentials)),
    ],
  );
}
