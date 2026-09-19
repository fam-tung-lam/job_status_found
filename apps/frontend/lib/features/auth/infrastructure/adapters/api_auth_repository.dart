import 'package:job_status_found/features/auth/application/dtos/token_pair_dto.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Auth repository backed by the backend API and HTTP package token store.
final class const ApiAuthRepository(
  /// Calls auth endpoints.
  final AuthApiClient _authApiClient,

  /// Owns token persistence.
  final JobStatusFoundHttpClient _httpClient, {

  /// Backend client-kind value.
  required final ClientKind _clientKind,
}) implements AuthRepository {
  /// Creates the repository for the supplied backend client kind.
  this;

  @override
  Future<SignedInUser?> restoreSession() async {
    try {
      if (_clientKind == ClientKind.web) {
        await _storeTokens(await _authApiClient.refreshWebSession());
      }
      return (await _authApiClient.fetchCurrentUser()).toEntity();
    } on JobStatusFoundHttpClientException catch (exception, stackTrace) {
      await _clearTokens();
      if (exception is JobStatusFoundHttpClientBadResponse &&
          (exception.statusCode == 401 ||
              exception.code == 'session_ended' ||
              exception.code == 'refresh_token_invalid')) {
        return null;
      }
      Error.throwWithStackTrace(_toFailure(exception), stackTrace);
    } on FormatException catch (_, stackTrace) {
      await _clearTokens();
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    } on Exception catch (_, stackTrace) {
      await _clearTokens();
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    }
  }

  @override
  Stream<AuthenticationStatus> watchAuthenticationStatus() async* {
    try {
      await for (final status in _httpClient.authenticationStatus) {
        yield switch (status) {
          JobStatusFoundAuthenticationStatus.initial =>
            AuthenticationStatus.initial,
          JobStatusFoundAuthenticationStatus.signedOut =>
            AuthenticationStatus.signedOut,
          JobStatusFoundAuthenticationStatus.signedIn =>
            AuthenticationStatus.signedIn,
        };
      }
    } on Exception catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    }
  }

  @override
  Future<SignedInUser> signInWithPassword({
    required EmailAddress email,
    required String password,
    required bool rememberMe,
  }) => _openSession(
    () => _authApiClient.signIn(
      email: email,
      password: password,
      clientKind: _clientKind,
      rememberMe: rememberMe,
    ),
  );

  @override
  Future<void> signUpWithPassword({
    required String firstName,
    required String lastName,
    required EmailAddress email,
    required String password,
  }) => _translate(
    () => _authApiClient.signUp(
      firstName: firstName,
      lastName: lastName,
      email: email,
      password: password,
    ),
  );

  @override
  Future<SignedInUser> confirmEmailVerification({
    required EmailAddress email,
    required String code,
    required String password,
    required bool rememberMe,
  }) => _openSession(
    () => _authApiClient.confirmEmail(
      email: email,
      code: code,
      password: password,
      clientKind: _clientKind,
      rememberMe: rememberMe,
    ),
  );

  @override
  Future<void> resendEmailVerification(EmailAddress email) =>
      _translate(() => _authApiClient.resendEmail(email));

  /// Stores tokens then resolves the current user, cleaning up partial state.
  Future<SignedInUser> _openSession(
    Future<TokenPairDTO> Function() createTokens,
  ) async {
    try {
      await _storeTokens(await createTokens());
      try {
        return (await _authApiClient.fetchCurrentUser()).toEntity();
      } on Exception {
        await _clearTokens();
        rethrow;
      }
    } on JobStatusFoundHttpClientException catch (exception, stackTrace) {
      Error.throwWithStackTrace(_toFailure(exception), stackTrace);
    } on FormatException catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    } on Exception catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    }
  }

  /// Persists the returned tokens.
  Future<void> _storeTokens(TokenPairDTO tokens) =>
      _httpClient.setTokens(tokens.toAuthTokens());

  /// Translates failures for an operation without a result.
  Future<void> _translate(Future<void> Function() operation) async {
    try {
      await operation();
    } on JobStatusFoundHttpClientException catch (exception, stackTrace) {
      Error.throwWithStackTrace(_toFailure(exception), stackTrace);
    } on FormatException catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    } on Exception catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    }
  }

  /// Maps the HTTP package hierarchy to auth-domain failures.
  AuthFailure _toFailure(JobStatusFoundHttpClientException exception) =>
      switch (exception) {
        JobStatusFoundHttpClientBadResponse(
          :final code,
          :final retryAfterSeconds,
        ) =>
          code == null
              ? const AuthServerUnreachableFailure()
              : AuthRejectedFailure(
                  AuthRejectionCode.fromWireName(code),
                  retryAfterSeconds: retryAfterSeconds,
                ),
        _ => const AuthServerUnreachableFailure(),
      };

  /// Deletes partial session state and maps storage failures to the auth
  /// domain.
  Future<void> _clearTokens() async {
    try {
      await _httpClient.clearTokens();
    } on Exception catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const AuthServerUnreachableFailure(),
        stackTrace,
      );
    }
  }
}
