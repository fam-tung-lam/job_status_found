import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/app/di.dart';
import 'package:job_status_found/features/health/health.dart';

void main() {
  late GetIt getIt;

  setUp(() {
    getIt = GetIt.asNewInstance();
  });

  tearDown(() async {
    await getIt.reset();
  });

  group('configureDependencies', () {
    test('makes the health check resolvable', () {
      // Given: settings that point at the local backend.
      final settings = AppSettings.fromApiBaseUrl('http://localhost:8000');

      // When: the app registers its dependencies.
      configureDependencies(getIt, settings);

      // Then: the home page's health check use case can be built from the
      // container.
      expect(getIt<CheckHealthUseCase>(), isA<CheckHealthUseCase>());
    });
  });
}
