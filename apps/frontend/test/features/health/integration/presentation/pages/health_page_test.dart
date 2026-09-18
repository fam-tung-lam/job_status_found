import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/features/health/presentation/pages/health_page.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../helpers/pump_app.dart';
import '../../../test_doubles/mock_job_status_found_http_client.dart';

/// The URL a failed health request reports in its
/// [JobStatusFoundHttpClientException].
final Uri _healthUrl = Uri.parse('http://localhost:8000/health');

void main() {
  group('HealthPage', () {
    late MockJobStatusFoundHttpClient httpClient;
    late HealthPage page;

    setUp(() {
      httpClient = MockJobStatusFoundHttpClient();
      page = HealthPage(
        checkHealth: CheckHealthUseCase(
          ApiHealthRepository(HealthApiClient(httpClient)),
        ),
      );
    });

    testWidgets('shows progress until the backend reports healthy', (
      tester,
    ) async {
      // Given: a backend that answers ok once the test releases it.
      final answer = Completer<Object?>();
      when(() => httpClient.get('/health')).thenAnswer((_) => answer.future);
      await tester.pumpApp(page);
      expect(find.text('Checking the backend…'), findsOneWidget);

      // When: the backend answers.
      answer.complete({'status': 'ok'});
      await tester.pump();

      // Then: the page says the backend is healthy.
      expect(find.text('The backend is healthy.'), findsOneWidget);
      expect(find.text('Checking the backend…'), findsNothing);
    });

    testWidgets('recovers when the user checks again after an outage', (
      tester,
    ) async {
      // Given: a backend that is down for the first check and up afterwards.
      final answers = <Future<Object?> Function()>[
        () async => throw JobStatusFoundHttpClientConnectionFailed(_healthUrl),
        () async => {'status': 'ok'},
      ];
      when(() => httpClient.get('/health'))
          .thenAnswer((_) => answers.removeAt(0)());
      await tester.pumpApp(page);
      await tester.pump();
      expect(
        find.text('Cannot reach the backend. Make sure it is running.'),
        findsOneWidget,
      );

      // When: the user asks to check again.
      await tester.tap(find.widgetWithText(FilledButton, 'Check again'));
      await tester.pump();

      // Then: the page says the backend is healthy.
      expect(find.text('The backend is healthy.'), findsOneWidget);
    });

    testWidgets('explains a response the app does not understand', (
      tester,
    ) async {
      // Given: a backend that answers with a server error.
      when(() => httpClient.get('/health')).thenThrow(
        JobStatusFoundHttpClientBadResponse(
          _healthUrl,
          statusCode: 500,
          body: {'detail': 'boom'},
        ),
      );

      // When: the page checks the backend.
      await tester.pumpApp(page);
      await tester.pump();

      // Then: the page says the response was not understood.
      expect(
        find.text('The backend sent a response this app does not understand.'),
        findsOneWidget,
      );
    });
  });
}
