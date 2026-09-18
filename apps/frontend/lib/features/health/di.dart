import 'package:get_it/get_it.dart';
import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/application/use_cases/check_health_use_case.dart';
import 'package:job_status_found/features/health/infrastructure/adapters/api_health_repository.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';
import 'package:job_status_found/settings.dart';

/// The name of the `get_it` scope that holds the health feature's
/// dependencies.
const healthFeatScopeName = 'health';

/// Registers the health feature in its own `get_it` scope.
extension HealthFeatScope on GetIt {
  /// Pushes a new final [healthFeatScopeName] scope that registers only the
  /// health feature's dependencies.
  ///
  /// Requires a [JobStatusFoundHttpClient] in a lower scope. Remove the
  /// feature with `dropScope(healthFeatScopeName)`. The feature reads nothing
  /// from [settings] yet.
  void pushHealthFeatScope(AppSettings settings) {
    pushNewScope(
      scopeName: healthFeatScopeName,
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
