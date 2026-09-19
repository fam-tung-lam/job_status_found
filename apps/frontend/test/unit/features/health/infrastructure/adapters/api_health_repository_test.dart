import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

void main() {
  group('ApiHealthRepository.checkBackendHealth', () {
    late MockJobStatusFoundHttpClient httpClient;
    late ApiHealthRepository repository;

    setUp(() {
      httpClient = MockJobStatusFoundHttpClient();
      repository = ApiHealthRepository(HealthApiClient(httpClient));
    });

    test('reports an unexpected response for an unknown status', () async {
      // Given: the backend reports a status this app does not know.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'degraded'});

      // When: the app checks the backend.
      final healthCheck = repository.checkBackendHealth();

      // Then: the check fails as an unexpected response.
      await expectLater(
        healthCheck,
        throwsA(const HealthCheckUnexpectedResponseFailure()),
      );
    });
  });
}
