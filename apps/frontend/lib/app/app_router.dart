import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/auth/auth.dart';
import 'package:job_status_found/features/home/home.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// The home page, which is the signed-in start page.
abstract final class HomeRoute._() {
  /// Prevents instances.
  this;

  /// Route name.
  static const name = 'home';

  /// Route path.
  static const path = '/';
}

/// Password sign-in route.
abstract final class SignInRoute._() {
  /// Prevents instances.
  this;

  /// Route name.
  static const name = 'sign-in';

  /// Route path.
  static const path = '/sign-in';

  /// Builds a location carrying a non-secret email.
  static String location(String email) => Uri(
    path: path,
    queryParameters: email.isEmpty ? null : {'email': email},
  ).toString();
}

/// Password sign-up route.
abstract final class SignUpRoute._() {
  /// Prevents instances.
  this;

  /// Route name.
  static const name = 'sign-up';

  /// Route path.
  static const path = '/sign-up';

  /// Builds a location carrying a non-secret email.
  static String location(String email) => Uri(
    path: path,
    queryParameters: email.isEmpty ? null : {'email': email},
  ).toString();
}

/// Email verification route.
abstract final class EmailVerificationRoute._() {
  /// Prevents instances.
  this;

  /// Route name.
  static const name = 'email-verification';

  /// Route path.
  static const path = '/verify-email';

  /// Builds a reload-safe location carrying only the email.
  static String location(String email) =>
      Uri(path: path, queryParameters: {'email': email}).toString();
}

/// Builds the guarded router over the app-wide [authSessionCubit].
GoRouter createAppRouter(GetIt getIt, AuthSessionCubit authSessionCubit) {
  final settings = getIt<AppSettings>();
  return GoRouter(
    initialLocation: HomeRoute.path,
    refreshListenable: _StreamListenable(authSessionCubit.stream),
    redirect: (_, state) {
      final session = authSessionCubit.state;
      if (session is AuthSessionRestoring) {
        return state.uri.path == _restoringPath
            ? null
            : _restoringLocation(state.uri);
      }
      final isAuthPage =
          state.uri.path == SignInRoute.path ||
          state.uri.path == SignUpRoute.path ||
          state.uri.path == EmailVerificationRoute.path;
      if (session is AuthSessionSignedOut) {
        if (state.uri.path == _restoringPath) {
          return _signedOutDestination(state.uri);
        }
        if (state.uri.path == EmailVerificationRoute.path &&
            EmailAddress.tryParse(state.uri.queryParameters['email'] ?? '') ==
                null) {
          return SignInRoute.path;
        }
        return isAuthPage ? null : SignInRoute.path;
      }
      if (session is AuthSessionSignedIn &&
          (isAuthPage || state.uri.path == _restoringPath)) {
        return HomeRoute.path;
      }
      return null;
    },
    routes: [
      GoRoute(
        path: _restoringPath,
        builder: (context, _) => Scaffold(
          body: Center(
            child: AppSpinner(
              semanticLabel: AppStrings.of(context).restoringSession,
            ),
          ),
        ),
      ),
      GoRoute(
        name: HomeRoute.name,
        path: HomeRoute.path,
        builder: (_, _) => HomePage(checkHealthUseCase: getIt()),
      ),
      GoRoute(
        name: SignInRoute.name,
        path: SignInRoute.path,
        builder: (context, state) => SignInPage(
          signInFormCubit: getIt(),
          initialEmail: state.uri.queryParameters['email'] ?? '',
          onRegister: (email) => context.go(SignUpRoute.location(email)),
          onVerificationRequired:
              ({required email, required password, required rememberMe}) =>
                  context.go(
                    EmailVerificationRoute.location(email),
                    extra: _EmailVerificationArguments(
                      password: password,
                      rememberMe: rememberMe,
                    ),
                  ),
        ),
      ),
      GoRoute(
        name: SignUpRoute.name,
        path: SignUpRoute.path,
        builder: (context, state) => SignUpPage(
          signUpFormCubit: getIt(),
          initialEmail: state.uri.queryParameters['email'] ?? '',
          termsUrl: settings.termsUrl,
          privacyUrl: settings.privacyUrl,
          onLogIn: (email) => context.go(SignInRoute.location(email)),
          onVerificationRequired: (email, password) => context.go(
            EmailVerificationRoute.location(email),
            extra: _EmailVerificationArguments(
              password: password,
              rememberMe: !kIsWeb,
            ),
          ),
        ),
      ),
      GoRoute(
        name: EmailVerificationRoute.name,
        path: EmailVerificationRoute.path,
        builder: (context, state) {
          final arguments = state.extra is _EmailVerificationArguments
              ? state.extra! as _EmailVerificationArguments
              : null;
          final email = EmailAddress.tryParse(
            state.uri.queryParameters['email'] ?? '',
          )!;
          return EmailVerificationPage(
            emailVerificationCubit: getIt(),
            email: email,
            initialPassword: arguments?.password ?? '',
            rememberMe: arguments?.rememberMe ?? !kIsWeb,
            onUseDifferentEmail: () =>
                context.go(SignInRoute.location(email.asTyped)),
          );
        },
      ),
    ],
  );
}

/// Internal path shown while session restoration is unresolved.
const _restoringPath = '/restoring-session';

/// Query parameter that retains a reload-safe startup destination.
const _restoringDestinationParameter = 'destination';

/// Builds the private restoring location without retaining route extras.
String _restoringLocation(Uri destination) => Uri(
  path: _restoringPath,
  queryParameters: {_restoringDestinationParameter: destination.toString()},
).toString();

/// Recovers an allowed auth destination after signed-out restoration.
String _signedOutDestination(Uri restoringUri) {
  final rawDestination =
      restoringUri.queryParameters[_restoringDestinationParameter];
  final destination = rawDestination == null
      ? null
      : Uri.tryParse(rawDestination);
  if (destination == null) return SignInRoute.path;
  if (destination.path == SignInRoute.path ||
      destination.path == SignUpRoute.path) {
    return destination.toString();
  }
  if (destination.path == EmailVerificationRoute.path &&
      EmailAddress.tryParse(destination.queryParameters['email'] ?? '') !=
          null) {
    return destination.toString();
  }
  return SignInRoute.path;
}

/// Secret route state that never enters the browser URL.
final class const _EmailVerificationArguments({
  /// Password submitted on the previous page.
  required final String password,

  /// Session persistence selected on the previous page.
  required final bool rememberMe,
}) {
  /// Creates ephemeral verification arguments.
  this;
}

/// Notifies GoRouter whenever the session stream emits.
final class _StreamListenable(Stream<Object?> stream) extends ChangeNotifier {
  /// Starts listening to [stream].
  this {
    _subscription = stream.listen((_) => notifyListeners());
  }

  /// Active session-state subscription.
  late final StreamSubscription<Object?> _subscription;
  @override
  void dispose() {
    unawaited(_subscription.cancel());
    super.dispose();
  }
}
