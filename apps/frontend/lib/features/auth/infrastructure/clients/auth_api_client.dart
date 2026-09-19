import 'package:job_status_found/features/auth/application/dtos/current_user_dto.dart';
import 'package:job_status_found/features/auth/application/dtos/token_pair_dto.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Calls the backend authentication endpoints.
final class const AuthApiClient(final JobStatusFoundHttpClient _httpClient) {
  /// Creates the client over the app HTTP client.
  this;

  /// Creates a password account.
  Future<void> signUp({
    required String firstName,
    required String lastName,
    required EmailAddress email,
    required String password,
  }) async {
    await _httpClient.post(
      '/v1/auth/sign-up',
      body: {
        'first_name': firstName,
        'last_name': lastName,
        'email': email.asTyped,
        'password': password,
      },
    );
  }

  /// Opens a session with password credentials.
  Future<TokenPairDTO> signIn({
    required EmailAddress email,
    required String password,
    required ClientKind clientKind,
    required bool rememberMe,
  }) async => _readTokenPair(
    await _httpClient.post(
      '/v1/auth/sign-in',
      body: {
        'email': email.asTyped,
        'password': password,
        'client_kind': clientKind.wireName,
        'remember_me': rememberMe,
      },
    ),
  );

  /// Opens a session after confirming the email code and password.
  Future<TokenPairDTO> confirmEmail({
    required EmailAddress email,
    required String code,
    required String password,
    required ClientKind clientKind,
    required bool rememberMe,
  }) async => _readTokenPair(
    await _httpClient.post(
      '/v1/auth/email-verification/confirm',
      body: {
        'email': email.asTyped,
        'code': code,
        'password': password,
        'client_kind': clientKind.wireName,
        'remember_me': rememberMe,
      },
    ),
  );

  /// Requests another verification code without revealing account state.
  Future<void> resendEmail(EmailAddress email) async {
    await _httpClient.post(
      '/v1/auth/email-verification/resend',
      body: {'email': email.asTyped},
    );
  }

  /// Refreshes a web cookie session explicitly after a reload.
  Future<TokenPairDTO> refreshWebSession() async =>
      _readTokenPair(await _httpClient.post('/v1/auth/token/refresh'));

  /// Reads the authenticated profile.
  Future<CurrentUserDTO> fetchCurrentUser() async {
    final body = await _httpClient.get('/v1/auth/me');
    if (body is! Map<String, Object?>) {
      throw const FormatException('Invalid current-user response.');
    }
    return CurrentUserDTO.fromJson(body);
  }

  /// Decodes one token-pair response.
  TokenPairDTO _readTokenPair(Object? body) {
    if (body is! Map<String, Object?>) {
      throw const FormatException('Invalid token pair.');
    }
    return TokenPairDTO.fromJson(body);
  }
}
