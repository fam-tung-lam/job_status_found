import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/di.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/settings.dart';

void main() {
  late GetIt getIt;

  setUp(() {
    getIt = GetIt.asNewInstance();
  });

  tearDown(() async {
    await getIt.reset();
  });

  group('configureDependencies', () {
    test('makes the health check resolvable from its feature scope', () {
      // Given: settings that point at the local backend.
      final settings = AppSettings.fromApiBaseUrl('http://localhost:8000');

      // When: the app registers its dependencies.
      configureDependencies(getIt, settings);

      // Then: the health feature has its scope, and the health page's use
      // case can be built from the container.
      expect(getIt.hasScope(healthFeatScopeName), isTrue);
      expect(getIt<CheckHealthUseCase>(), isA<CheckHealthUseCase>());
    });
  });
}
