import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

import '../../../../test_doubles/in_memory_job_status_found_token_storage.dart';

/// Answers [request] with [statusCode] and [body] encoded as JSON.
Future<void> _respondJson(
  HttpRequest request,
  int statusCode,
  Object? body,
) async {
  request.response
    ..statusCode = statusCode
    ..headers.contentType = ContentType.json
    ..write(jsonEncode(body));
  await request.response.close();
}

void main() {
  late HttpServer server;
  late FutureOr<void> Function(HttpRequest request) respond;
  late DioJobStatusFoundHttpClient client;

  setUp(() async {
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0)
      ..listen((request) => respond(request));
    client = DioJobStatusFoundHttpClient(
      baseUrl: Uri.parse('http://${server.address.host}:${server.port}'),
      tokenStorage: InMemoryJobStatusFoundTokenStorage(),
      receiveTimeout: const Duration(seconds: 1),
    );
  });

  tearDown(() async {
    client.close();
    await server.close(force: true);
  });

  group('DioJobStatusFoundHttpClient.get', () {
    test('returns the decoded JSON body of a 2xx response', () async {
      // Given: a server that echoes the requested path and query.
      respond = (request) => _respondJson(request, 200, {
        'path': request.uri.path,
        'query': request.uri.queryParameters,
      });

      // When: the client requests a path with a query parameter.
      final body = await client.get(
        '/jobs',
        queryParameters: {'status': 'open'},
      );

      // Then: the body is the decoded JSON the server sent for that request.
      expect(body, {
        'path': '/jobs',
        'query': {'status': 'open'},
      });
    });

    test('reports a 4xx as a bad response with its status and body', () async {
      // Given: a server that rejects every request as not found.
      respond = (request) =>
          _respondJson(request, 404, {'detail': 'Not Found'});

      // When: the client requests a missing path.
      final pendingRequest = client.get('/missing');

      // Then: the failure carries the status code and the decoded body.
      await expectLater(
        pendingRequest,
        throwsA(
          isA<JobStatusFoundHttpClientBadResponse>()
              .having((failure) => failure.statusCode, 'statusCode', 404)
              .having((failure) => failure.body, 'body', {
                'detail': 'Not Found',
              })
              .having(
                (failure) => failure.requestUri.path,
                'requestUri.path',
                '/missing',
              ),
        ),
      );
    });

    test('reports a connection failure when nothing listens', () async {
      // Given: the server has stopped, so nothing listens on its port.
      await server.close(force: true);

      // When: the client sends a request there.
      final pendingRequest = client.get('/health');

      // Then: the request fails as a connection failure.
      await expectLater(
        pendingRequest,
        throwsA(isA<JobStatusFoundHttpClientConnectionFailed>()),
      );
    });

    test('reports a receive timeout when the response is too slow', () async {
      // Given: a server that holds every request open without answering.
      respond = (_) {};

      // When: the client waits longer than its receive timeout.
      final pendingRequest = client.get('/slow');

      // Then: the request fails as a receive timeout.
      await expectLater(
        pendingRequest,
        throwsA(isA<JobStatusFoundHttpClientReceiveTimeout>()),
      );
    });
  });

  group('DioJobStatusFoundHttpClient authentication', () {
    test('does not attach or refresh tokens for password sign-in', () async {
      // Given: stored tokens and a sign-in endpoint that rejects credentials.
      await client.setTokens(
        JobStatusFoundAuthTokens(
          accessToken: 'old-access',
          refreshToken: 'old-refresh',
          expiresIn: 3600,
          tokenType: JobStatusFoundAuthTokenType.bearer,
          issuedAt: DateTime.now(),
        ),
      );
      var requestCount = 0;
      String? authorization;
      respond = (request) {
        requestCount += 1;
        authorization = request.headers.value(HttpHeaders.authorizationHeader);
        return _respondJson(request, 401, {'code': 'invalid_credentials'});
      };

      // When: password sign-in receives a 401.
      final pendingRequest = client.post(
        '/v1/auth/sign-in',
        body: {'email': 'person@example.com', 'password': 'wrong'},
      );

      // Then: Fresh neither attaches the old session nor calls refresh.
      await expectLater(
        pendingRequest,
        throwsA(
          isA<JobStatusFoundHttpClientBadResponse>().having(
            (failure) => failure.code,
            'code',
            'invalid_credentials',
          ),
        ),
      );
      expect(requestCount, 1);
      expect(authorization, isNull);
    });

    test('refreshes once and retries a protected request', () async {
      // Given: a protected request whose old access token receives a 401.
      await client.setTokens(
        JobStatusFoundAuthTokens(
          accessToken: 'old-access',
          refreshToken: 'old-refresh',
          expiresIn: 3600,
          tokenType: JobStatusFoundAuthTokenType.bearer,
          issuedAt: DateTime.now(),
        ),
      );
      final paths = <String>[];
      final authorizations = <String?>[];
      respond = (request) {
        paths.add(request.uri.path);
        authorizations.add(
          request.headers.value(HttpHeaders.authorizationHeader),
        );
        if (request.uri.path == '/v1/auth/token/refresh') {
          return _respondJson(request, 200, {
            'access_token': 'new-access',
            'refresh_token': 'new-refresh',
            'expires_in': 900,
            'token_type': 'Bearer',
          });
        }
        if (paths.where((path) => path == '/protected').length == 1) {
          return _respondJson(request, 401, {'code': 'access_token_invalid'});
        }
        return _respondJson(request, 200, {'status': 'ok'});
      };

      // When: the protected request is sent.
      final body = await client.get('/protected');

      // Then: one refresh rotates the token before the one retry.
      expect(body, {'status': 'ok'});
      expect(paths, ['/protected', '/v1/auth/token/refresh', '/protected']);
      expect(authorizations.first, 'Bearer old-access');
      expect(authorizations.last, 'Bearer new-access');
    });
  });
}
