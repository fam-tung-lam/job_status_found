import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

import '../../../test_doubles/mock_job_status_found_http_client.dart';

void main() {
  late GetIt getIt;
  late AppSettings settings;

  setUp(() {
    getIt = GetIt.asNewInstance()
      ..registerSingleton<JobStatusFoundHttpClient>(
        MockJobStatusFoundHttpClient(),
      );
    settings = AppSettings.fromApiBaseUrl('http://localhost:8000');
  });

  tearDown(() async {
    await getIt.reset();
  });

  group('GetIt.pushHealthFeatScope', () {
    test('adds the health check on top of the shared HTTP client', () {
      // Given: a container that holds only the shared HTTP client.

      // When: the health feature pushes its scope.
      getIt.pushHealthFeatScope(settings);

      // Then: the health check resolves from the health scope.
      expect(getIt.currentScopeName, healthFeatScopeName);
      expect(getIt.isRegistered<CheckHealthUseCase>(), isTrue);
    });

    test('removes the health check when its scope is dropped', () async {
      // Given: the health feature is registered.
      getIt.pushHealthFeatScope(settings);

      // When: the health scope is dropped.
      await getIt.dropScope(healthFeatScopeName);

      // Then: the health check is gone and the shared client remains.
      expect(getIt.isRegistered<CheckHealthUseCase>(), isFalse);
      expect(getIt.isRegistered<JobStatusFoundHttpClient>(), isTrue);
    });
  });
}
