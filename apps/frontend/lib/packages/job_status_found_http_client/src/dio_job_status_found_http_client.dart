import 'dart:async';

import 'package:dio/dio.dart';
import 'package:fresh_dio/fresh_dio.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/configure_http_client_adapter.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client_exception.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_token_storage.dart';

/// [JobStatusFoundHttpClient] backed by Dio with transparent token refresh.
final class const DioJobStatusFoundHttpClient._(
  /// Sends ordinary API requests.
  final Dio _dio,

  /// Sends refresh calls and one-time retries.
  final Dio _refreshDio,

  /// Attaches, refreshes, and persists authentication tokens.
  final Fresh<_AuthToken> _fresh,
) implements JobStatusFoundHttpClient {
  /// Creates the authenticated client and its separate refresh client.
  factory({
    required Uri baseUrl,
    required JobStatusFoundTokenStorage tokenStorage,
    Duration connectTimeout = const Duration(seconds: 5),
    Duration sendTimeout = const Duration(seconds: 5),
    Duration receiveTimeout = const Duration(seconds: 10),
  }) {
    final dio = Dio(
      BaseOptions(
        baseUrl: baseUrl.toString(),
        connectTimeout: connectTimeout,
        sendTimeout: sendTimeout,
        receiveTimeout: receiveTimeout,
      ),
    );
    final refreshDio = Dio(
      BaseOptions(
        baseUrl: baseUrl.toString(),
        connectTimeout: connectTimeout,
        sendTimeout: sendTimeout,
        receiveTimeout: receiveTimeout,
      ),
    );
    configureHttpClientAdapter(dio);
    configureHttpClientAdapter(refreshDio);
    final fresh = Fresh.oAuth2<_AuthToken>(
      tokenStorage: _FreshTokenStorage(tokenStorage),
      httpClient: refreshDio,
      isTokenRequired: (request) => request.extra['requires_auth'] == true,
      refreshToken: (token, client) async {
        try {
          final response = await client.post<Object?>(
            '/v1/auth/token/refresh',
            data: token?.refreshToken == null
                ? null
                : {'refresh_token': token!.refreshToken},
          );
          return _AuthToken.fromResponse(response.data);
        } on DioException catch (exception) {
          final code = _problemCode(exception.response?.data);
          if (code == 'refresh_token_invalid' || code == 'session_ended') {
            throw RevokeTokenException();
          }
          rethrow;
        }
      },
    );
    dio.interceptors.add(fresh);
    return DioJobStatusFoundHttpClient._(dio, refreshDio, fresh);
  }

  /// Stores configured clients and the interceptor.
  this;

  @override
  Stream<JobStatusFoundAuthenticationStatus> get authenticationStatus =>
      _fresh.authenticationStatus.map(
        (status) => switch (status) {
          AuthenticationStatus.initial =>
            JobStatusFoundAuthenticationStatus.initial,
          AuthenticationStatus.unauthenticated =>
            JobStatusFoundAuthenticationStatus.signedOut,
          AuthenticationStatus.authenticated =>
            JobStatusFoundAuthenticationStatus.signedIn,
        },
      );

  @override
  Future<Object?> get(
    String path, {
    Map<String, Object?> queryParameters = const {},
  }) => _send(
    () => _dio.get<Object?>(
      path,
      queryParameters: queryParameters,
      options: Options(extra: {'requires_auth': true}),
    ),
  );

  @override
  Future<Object?> post(String path, {Object? body}) => _send(
    () => _dio.post<Object?>(
      path,
      data: body,
      options: Options(extra: {'requires_auth': !_isPublicPath(path)}),
    ),
  );

  @override
  Future<Object?> put(String path, {Object? body}) => _send(
    () => _dio.put<Object?>(
      path,
      data: body,
      options: Options(extra: {'requires_auth': true}),
    ),
  );

  @override
  Future<Object?> delete(String path, {Object? body}) => _send(
    () => _dio.delete<Object?>(
      path,
      data: body,
      options: Options(extra: {'requires_auth': true}),
    ),
  );

  @override
  Future<void> setTokens(JobStatusFoundAuthTokens tokens) =>
      _fresh.setToken(_AuthToken.fromPublic(tokens));

  @override
  Future<void> clearTokens() => _fresh.clearToken();

  /// Sends one request and translates Dio failures.
  Future<Object?> _send(Future<Response<Object?>> Function() send) async {
    try {
      return (await send()).data;
    } on DioException catch (exception, stackTrace) {
      Error.throwWithStackTrace(_toClientException(exception), stackTrace);
    }
  }

  @override
  void close() {
    _dio.close();
    _refreshDio.close();
    unawaited(_fresh.close());
  }

  /// Converts one Dio failure to the public exception hierarchy.
  JobStatusFoundHttpClientException _toClientException(DioException exception) {
    final requestUri = exception.requestOptions.uri;
    return switch (exception.type) {
      DioExceptionType.connectionTimeout =>
        JobStatusFoundHttpClientConnectionTimeout(requestUri),
      DioExceptionType.sendTimeout => JobStatusFoundHttpClientSendTimeout(
        requestUri,
      ),
      DioExceptionType.receiveTimeout => JobStatusFoundHttpClientReceiveTimeout(
        requestUri,
      ),
      DioExceptionType.badCertificate => JobStatusFoundHttpClientBadCertificate(
        requestUri,
      ),
      DioExceptionType.badResponse => JobStatusFoundHttpClientBadResponse(
        requestUri,
        statusCode: exception.response?.statusCode,
        body: exception.response?.data,
        code: _problemCode(exception.response?.data),
        retryAfterSeconds: int.tryParse(
          exception.response?.headers.value('retry-after') ?? '',
        ),
      ),
      DioExceptionType.cancel => JobStatusFoundHttpClientCancelled(requestUri),
      DioExceptionType.connectionError =>
        JobStatusFoundHttpClientConnectionFailed(requestUri),
      DioExceptionType.transformTimeout =>
        JobStatusFoundHttpClientTransformTimeout(requestUri),
      DioExceptionType.unknown => JobStatusFoundHttpClientUnknownFailure(
        requestUri,
        cause: exception.error,
      ),
    };
  }
}

/// Fresh token retaining the API's expiry metadata.
final class const _AuthToken({
  required super.accessToken,
  required super.refreshToken,
  required super.expiresIn,
  required super.tokenType,
  required super.issuedAt,
}) extends OAuth2Token {
  /// Creates one Fresh token.
  this;

  /// Converts package tokens to Fresh tokens.
  factory fromPublic(JobStatusFoundAuthTokens tokens) => _AuthToken(
    accessToken: tokens.accessToken,
    refreshToken: tokens.refreshToken,
    expiresIn: tokens.expiresIn,
    tokenType: tokens.tokenType.wireName,
    issuedAt: tokens.issuedAt,
  );

  /// Decodes a backend token pair.
  factory fromResponse(Object? body) {
    if (body is! Map<String, Object?> ||
        body['access_token'] is! String ||
        body['expires_in'] is! int ||
        body['token_type'] is! String) {
      throw const FormatException('Expected a token-pair JSON object.');
    }
    final tokenType = JobStatusFoundAuthTokenType.tryFromWireName(
      body['token_type']! as String,
    );
    if (tokenType == null) {
      throw const FormatException('Expected a supported token type.');
    }
    return _AuthToken(
      accessToken: body['access_token']! as String,
      refreshToken: body['refresh_token'] as String?,
      expiresIn: body['expires_in']! as int,
      tokenType: tokenType.wireName,
      issuedAt: DateTime.now(),
    );
  }

  /// Converts to the package storage type.
  JobStatusFoundAuthTokens toPublic() => JobStatusFoundAuthTokens(
    accessToken: accessToken,
    refreshToken: refreshToken,
    expiresIn: expiresIn!,
    tokenType: JobStatusFoundAuthTokenType.tryFromWireName(tokenType!)!,
    issuedAt: issuedAt!,
  );
}

/// Adapts package token storage to Fresh without exposing Fresh publicly.
final class const _FreshTokenStorage(
  /// Stores public token values.
  final JobStatusFoundTokenStorage _storage,
) implements TokenStorage<_AuthToken> {
  @override
  Future<void> delete() => _storage.delete();

  @override
  Future<_AuthToken?> read() async {
    final tokens = await _storage.read();
    return tokens == null ? null : _AuthToken.fromPublic(tokens);
  }

  @override
  Future<void> write(_AuthToken token) => _storage.write(token.toPublic());
}

/// Reads a stable code from an RFC 9457 body.
String? _problemCode(Object? body) =>
    body is Map<String, Object?> ? body['code'] as String? : null;

/// Whether [path] creates or restores authentication without a bearer token.
bool _isPublicPath(String path) => const {
  '/v1/auth/sign-up',
  '/v1/auth/sign-in',
  '/v1/auth/email-verification/confirm',
  '/v1/auth/email-verification/resend',
  '/v1/auth/token/refresh',
}.contains(path);
