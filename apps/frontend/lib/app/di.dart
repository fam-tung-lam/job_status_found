import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Registers every app dependency in [getIt], built from [settings]: shared
/// packages in the base scope, then each feature in a scope of its own.
void configureDependencies(GetIt getIt, AppSettings settings) {
  getIt
    ..registerLazySingleton<JobStatusFoundHttpClient>(
      () => DioJobStatusFoundHttpClient(baseUrl: settings.apiBaseUrl),
      dispose: (httpClient) => httpClient.close(),
    )
    ..pushHealthFeatureScope(settings);
}
