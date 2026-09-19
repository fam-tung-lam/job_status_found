import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_cubit.dart';
import 'package:job_status_found/features/health/presentation/bloc/health_status_state.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../../test_doubles/mock_job_status_found_http_client.dart';

/// URL reported by failed health requests.
final Uri _healthUrl = Uri.parse('http://localhost:8000/health');

/// Builds the complete health flow above the mocked HTTP boundary.
HealthStatusCubit _buildCubit(MockJobStatusFoundHttpClient httpClient) =>
    HealthStatusCubit(
      CheckHealthUseCase(ApiHealthRepository(HealthApiClient(httpClient))),
    );

void main() {
  late MockJobStatusFoundHttpClient httpClient;

  setUp(() {
    httpClient = MockJobStatusFoundHttpClient();
  });

  blocTest<HealthStatusCubit, HealthStatusState>(
    'reports healthy after the API returns ok',
    setUp: () {
      // Given: the lowest HTTP boundary returns the documented health body.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'ok'});
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) {
      // When: the Cubit checks the backend.
      return cubit.checkBackendHealth();
    },
    expect: () => const [
      // Then: the Cubit exposes progress followed by success.
      HealthStatusChecking(),
      HealthStatusHealthy(),
    ],
  );

  blocTest<HealthStatusCubit, HealthStatusState>(
    'recovers when a second API check succeeds after an outage',
    setUp: () {
      // Given: the lowest HTTP boundary fails once and then returns ok.
      final responses = <Future<Object?> Function()>[
        () async => throw JobStatusFoundHttpClientConnectionFailed(_healthUrl),
        () async => {'status': 'ok'},
      ];
      when(() => httpClient.get('/health'))
          .thenAnswer((_) => responses.removeAt(0)());
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) async {
      // When: the Cubit checks again after the failed request.
      await cubit.checkBackendHealth();
      await cubit.checkBackendHealth();
    },
    expect: () => const [
      // Then: the complete flow reports the outage and later recovery.
      HealthStatusChecking(),
      HealthStatusCheckFailed(HealthCheckBackendUnreachableFailure()),
      HealthStatusChecking(),
      HealthStatusHealthy(),
    ],
  );

  blocTest<HealthStatusCubit, HealthStatusState>(
    'reports an unexpected response for an unknown API status',
    setUp: () {
      // Given: the lowest HTTP boundary returns an unsupported status.
      when(() => httpClient.get('/health'))
          .thenAnswer((_) async => {'status': 'degraded'});
    },
    build: () => _buildCubit(httpClient),
    act: (cubit) {
      // When: the Cubit checks the backend.
      return cubit.checkBackendHealth();
    },
    expect: () => const [
      // Then: the Cubit exposes the mapped domain failure.
      HealthStatusChecking(),
      HealthStatusCheckFailed(HealthCheckUnexpectedResponseFailure()),
    ],
  );
}
