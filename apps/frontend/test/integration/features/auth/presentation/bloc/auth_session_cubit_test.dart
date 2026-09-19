import 'dart:async';

import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/use_cases/restore_session_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/watch_authentication_status_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_state.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// Profile returned by the lowest HTTP boundary.
const _currentUserResponse = <String, Object?>{
  'id': 'id',
  'email': 'person@example.com',
  'first_name': 'Pat',
  'last_name': 'Lee',
  'avatar_url': null,
  'locale': null,
  'role': 'user',
  'has_password': true,
  'linked_providers': <Object?>[],
};

/// Domain user decoded from [_currentUserResponse].
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

/// Builds the complete session flow above the mocked HTTP boundary.
AuthSessionCubit _buildCubit(MockJobStatusFoundHttpClient httpClient) {
  final repository = ApiAuthRepository(
    AuthApiClient(httpClient),
    httpClient,
    clientKind: ClientKind.android,
  );
  return AuthSessionCubit(
    RestoreSessionUseCase(repository),
    WatchAuthenticationStatusUseCase(repository),
  );
}

void main() {
  late MockJobStatusFoundHttpClient httpClient;
  late Completer<JobStatusFoundAuthenticationStatus> authenticationStatus;

  setUp(() {
    httpClient = MockJobStatusFoundHttpClient();
  });

  blocTest<AuthSessionCubit, AuthSessionState>(
    'restores the API user then reacts to token revocation',
    setUp: () {
      // Given: the lowest HTTP boundary returns a valid signed-in profile.
      authenticationStatus = Completer<JobStatusFoundAuthenticationStatus>();
      when(() => httpClient.authenticationStatus)
          .thenAnswer((_) => Stream.fromFuture(authenticationStatus.future));
      when(() => httpClient.get('/v1/auth/me'))
          .thenAnswer((_) async => _currentUserResponse);
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) async {
      // When: startup restoration completes and token storage revokes access.
      await cubit.restoreSession();
      authenticationStatus.complete(
        JobStatusFoundAuthenticationStatus.signedOut,
      );
      await Future<void>.delayed(Duration.zero);
    },
    expect: () => [
      // Then: the Cubit publishes the restored user and the later sign-out.
      AuthSessionSignedIn(_user),
      const AuthSessionSignedOut(),
    ],
  );

  blocTest<AuthSessionCubit, AuthSessionState>(
    'maps a lowest-boundary status failure to signed out',
    setUp: () {
      // Given: credential observation fails at the HTTP boundary.
      when(() => httpClient.authenticationStatus).thenAnswer(
        (_) => Stream<JobStatusFoundAuthenticationStatus>.error(
          Exception('storage'),
        ),
      );
    },
    build: () => _buildCubit(httpClient),
    act: (_) async {
      // When: the mapped failure reaches the Cubit.
      await Future<void>.delayed(Duration.zero);
    },
    expect: () => const [
      // Then: the Cubit exposes the safe signed-out state.
      AuthSessionSignedOut(),
    ],
  );
}
