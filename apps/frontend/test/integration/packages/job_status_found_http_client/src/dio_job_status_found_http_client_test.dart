import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

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
      final request = client.get('/missing');

      // Then: the failure carries the status code and the decoded body.
      await expectLater(
        request,
        throwsA(
          isA<JobStatusFoundHttpClientBadResponse>()
              .having((e) => e.statusCode, 'statusCode', 404)
              .having((e) => e.body, 'body', {'detail': 'Not Found'})
              .having((e) => e.uri.path, 'uri.path', '/missing'),
        ),
      );
    });

    test('reports a connection failure when nothing listens', () async {
      // Given: the server has stopped, so nothing listens on its port.
      await server.close(force: true);

      // When: the client sends a request there.
      final request = client.get('/health');

      // Then: the request fails as a connection failure.
      await expectLater(
        request,
        throwsA(isA<JobStatusFoundHttpClientConnectionFailed>()),
      );
    });

    test('reports a receive timeout when the response is too slow', () async {
      // Given: a server that holds every request open without answering.
      respond = (_) {};

      // When: the client waits longer than its receive timeout.
      final request = client.get('/slow');

      // Then: the request fails as a receive timeout.
      await expectLater(
        request,
        throwsA(isA<JobStatusFoundHttpClientReceiveTimeout>()),
      );
    });
  });
}
