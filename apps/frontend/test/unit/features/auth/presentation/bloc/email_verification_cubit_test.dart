import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_state.dart';
import 'package:mocktail/mocktail.dart';

/// Auth boundary controlled by verification tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

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
  late _MockAuthRepository repository;
  late SignedInUser? signedInUser;

  setUp(() {
    repository = _MockAuthRepository();
    signedInUser = null;
  });

  blocTest<EmailVerificationCubit, EmailVerificationState>(
    'confirms the code with the password and original persistence choice',
    setUp: () {
      when(
        () => repository.confirmEmailVerification(
          email: email,
          code: '012345',
          password: 'matching password',
          rememberMe: true,
        ),
      ).thenAnswer((_) async => user);
    },
    build: () => EmailVerificationCubit(
      ConfirmEmailVerificationUseCase(repository),
      ResendEmailVerificationUseCase(repository),
      (user) => signedInUser = user,
    ),
    act: (cubit) => cubit.confirm(
      email: email,
      code: '012345',
      password: 'matching password',
      rememberMe: true,
    ),
    expect: () => const [EmailVerificationSubmitting(60)],
    verify: (_) => expect(signedInUser, user),
  );
}
