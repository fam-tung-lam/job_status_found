import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// The URL a failed health request reports in its
/// [JobStatusFoundHttpClientException].
final Uri _healthUrl = Uri.parse('http://localhost:8000/health');

void main() {
  group('ApiHealthRepository.check', () {
    late MockJobStatusFoundHttpClient httpClient;
    late ApiHealthRepository repository;

    setUp(() {
      httpClient = MockJobStatusFoundHttpClient();
      repository = ApiHealthRepository(HealthApiClient(httpClient));
    });

    test('completes normally when GET /health answers ok', () async {
      // Given: the backend reports that it is alive.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'ok'});

      // When: the app checks the backend.
      final check = repository.check();

      // Then: the check completes without a failure.
      await expectLater(check, completes);
    });

    test('reports unreachable when the connection fails', () async {
      // Given: nothing answers at the backend URL.
      when(() => httpClient.get('/health'))
          .thenThrow(JobStatusFoundHttpClientConnectionFailed(_healthUrl));

      // When: the app checks the backend.
      final check = repository.check();

      // Then: the check fails as unreachable.
      await expectLater(check, throwsA(const HealthCheckBackendUnreachable()));
    });

    test('reports an unexpected response for a server error', () async {
      // Given: the backend fails while answering.
      when(() => httpClient.get('/health')).thenThrow(
        JobStatusFoundHttpClientBadResponse(
          _healthUrl,
          statusCode: 500,
          body: {'detail': 'boom'},
        ),
      );

      // When: the app checks the backend.
      final check = repository.check();

      // Then: the check fails as an unexpected response.
      await expectLater(check, throwsA(const HealthCheckUnexpectedResponse()));
    });

    test('reports an unexpected response for an unknown status', () async {
      // Given: the backend reports a status this app does not know.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'degraded'});

      // When: the app checks the backend.
      final check = repository.check();

      // Then: the check fails as an unexpected response.
      await expectLater(check, throwsA(const HealthCheckUnexpectedResponse()));
    });
  });
}
