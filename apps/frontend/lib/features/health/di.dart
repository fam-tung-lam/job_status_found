import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// The name of the `get_it` scope that holds the health feature's
/// dependencies.
const healthFeatureScopeName = 'health';

/// Registers the health feature in its own `get_it` scope.
extension HealthFeatureScope on GetIt {
  /// Pushes a new final [healthFeatureScopeName] scope that registers only the
  /// health feature's dependencies.
  ///
  /// Requires a [JobStatusFoundHttpClient] in a lower scope. Remove the
  /// feature with `dropScope(healthFeatureScopeName)`. The feature reads
  /// nothing from [settings] yet.
  void pushHealthFeatureScope(AppSettings settings) {
    pushNewScope(
      scopeName: healthFeatureScopeName,
      isFinal: true,
      init: (scope) => scope
        ..registerLazySingleton(() => HealthApiClient(scope()))
        ..registerLazySingleton<HealthRepository>(
          () => ApiHealthRepository(scope()),
        )
        ..registerFactory(() => CheckHealthUseCase(scope())),
    );
  }
}
