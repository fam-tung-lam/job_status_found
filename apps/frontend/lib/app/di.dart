import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/auth/auth.dart';
import 'package:job_status_found/features/health/health.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Registers every app dependency in [getIt], built from [settings]: shared
/// packages in the base scope, then each feature in a scope of its own.
void configureDependencies(
  GetIt getIt,
  AppSettings settings, {
  JobStatusFoundTokenStorage? tokenStorage,
}) {
  final resolvedTokenStorage =
      tokenStorage ??
      const SecureJobStatusFoundTokenStorage(FlutterSecureStorage());
  getIt
    ..registerSingleton<AppSettings>(settings)
    ..registerSingleton<JobStatusFoundTokenStorage>(resolvedTokenStorage)
    ..registerLazySingleton<JobStatusFoundHttpClient>(
      () => DioJobStatusFoundHttpClient(
        baseUrl: settings.apiBaseUrl,
        tokenStorage: getIt(),
      ),
      dispose: (httpClient) => httpClient.close(),
    )
    ..pushAuthFeatureScope(settings)
    ..pushHealthFeatureScope(settings);
}
