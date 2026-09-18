import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:job_status_found/features/health/health.dart';

/// The backend health page, which is the app's start page for now.
abstract final class HealthRoute._() {
  /// Prevents instances; the class only holds route constants.
  this;

  /// The route name.
  static const name = 'health';

  /// The route path.
  static const path = '/';
}

/// Builds the app router, resolving each page's dependencies from [getIt].
GoRouter createAppRouter(GetIt getIt) => GoRouter(
  initialLocation: HealthRoute.path,
  routes: [
    GoRoute(
      name: HealthRoute.name,
      path: HealthRoute.path,
      builder: (_, _) => HealthPage(checkHealth: getIt()),
    ),
  ],
);
