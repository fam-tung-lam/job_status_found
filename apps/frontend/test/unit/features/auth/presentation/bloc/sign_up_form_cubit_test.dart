import 'package:bloc_test/bloc_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_state.dart';
import 'package:mocktail/mocktail.dart';

/// Auth repository controlled by sign-up tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

void main() {
  final email = EmailAddress.tryParse('person@example.com')!;
  blocTest<SignUpFormCubit, SignUpFormState>(
    'carries accepted email and password to verification',
    build: () {
      final repository = _MockAuthRepository();
      when(
        () => repository.signUpWithPassword(
          firstName: 'Pat',
          lastName: 'Lee',
          email: email,
          password: 'secure password',
        ),
      ).thenAnswer((_) async {});
      return SignUpFormCubit(SignUpWithPasswordUseCase(repository));
    },
    act: (cubit) => cubit.submit(
      firstName: 'Pat',
      lastName: 'Lee',
      email: email,
      password: 'secure password',
    ),
    expect: () => [
      const SignUpFormSubmitting(),
      SignUpFormVerificationRequired(email, 'secure password'),
    ],
  );
}
