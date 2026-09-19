import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/restore_session_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/watch_authentication_status_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_state.dart';
import 'package:mocktail/mocktail.dart';

/// Auth repository controlled by session tests.
final class _MockAuthRepository() extends Mock implements AuthRepository;

/// Current user returned by the restoration stub.
final _user = SignedInUser(
  id: 'id',
  email: EmailAddress.tryParse('person@example.com')!,
  firstName: 'Pat',
  lastName: 'Lee',
  avatarUrl: null,
  locale: null,
  role: UserRole.user,
  hasPassword: true,
  linkedProviders: const [],
);

/// Answers restoration with [_user].
Future<SignedInUser> _restoreUser(Invocation _) async => _user;

void main() {
  test('restores a user then reacts to token revocation', () async {
    // Given: a restorable session and its token-status stream.
    final repository = _MockAuthRepository();
    when(repository.restoreSession).thenAnswer(_restoreUser);
    final statuses = StreamController<AuthenticationStatus>.broadcast();
    when(repository.watchAuthenticationStatus)
        .thenAnswer((_) => statuses.stream);
    final cubit = AuthSessionCubit(
      RestoreSessionUseCase(repository),
      WatchAuthenticationStatusUseCase(repository),
    );
    expect(cubit.state, const AuthSessionRestoring());

    // When: startup restoration completes.
    await cubit.restoreSession();

    // Then: the current user owns the signed-in state.
    expect(cubit.state, AuthSessionSignedIn(_user));

    // When: token refresh reports revocation.
    statuses.add(AuthenticationStatus.signedOut);
    await Future<void>.delayed(Duration.zero);

    // Then: the session returns to signed out.
    expect(cubit.state, const AuthSessionSignedOut());
    await cubit.close();
    await statuses.close();
  });

  test('maps an authentication-status domain failure to signed out', () async {
    // Given: credential observation fails at the repository boundary.
    final repository = _MockAuthRepository();
    when(repository.watchAuthenticationStatus).thenAnswer(
      (_) => Stream<AuthenticationStatus>.error(
        const AuthServerUnreachableFailure(),
      ),
    );
    final cubit = AuthSessionCubit(
      RestoreSessionUseCase(repository),
      WatchAuthenticationStatusUseCase(repository),
    );

    // When: the domain failure reaches the cubit.
    await Future<void>.delayed(Duration.zero);

    // Then: the UI receives the safe signed-out state.
    expect(cubit.state, const AuthSessionSignedOut());
    await cubit.close();
  });
}
