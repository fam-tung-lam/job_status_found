import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:job_status_found/features/home/home.dart';

/// The home page, which is the app's start page.
abstract final class HomeRoute._() {
  /// Prevents instances; the class only holds route constants.
  this;

  /// The route name.
  static const name = 'home';

  /// The route path.
  static const path = '/';
}

/// Builds the app router, resolving each page's dependencies from [getIt].
GoRouter createAppRouter(GetIt getIt) => GoRouter(
  initialLocation: HomeRoute.path,
  routes: [
    GoRoute(
      name: HomeRoute.name,
      path: HomeRoute.path,
      builder: (_, _) => HomePage(checkHealthUseCase: getIt()),
    ),
  ],
);
