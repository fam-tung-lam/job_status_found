import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/features/auth/application/ports/auth_repository.dart';
import 'package:job_status_found/features/auth/application/use_cases/confirm_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/resend_email_verification_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/restore_session_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_in_with_password_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/sign_up_with_password_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/watch_authentication_status_use_case.dart';
import 'package:job_status_found/features/auth/infrastructure/adapters/api_auth_repository.dart';
import 'package:job_status_found/features/auth/infrastructure/clients/auth_api_client.dart';
import 'package:job_status_found/features/auth/infrastructure/helpers/read_client_kind.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/email_verification_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_in_form_cubit.dart';
import 'package:job_status_found/features/auth/presentation/bloc/sign_up_form_cubit.dart';

/// Name of the dependency scope holding authentication.
const authFeatureScopeName = 'auth';

/// Registers authentication dependencies.
extension AuthFeatureScope on GetIt {
  /// Pushes the final auth scope over the shared HTTP client.
  void pushAuthFeatureScope(AppSettings settings) {
    pushNewScope(
      scopeName: authFeatureScopeName,
      isFinal: true,
      init: (scope) => scope
        ..registerLazySingleton(() => AuthApiClient(scope()))
        ..registerLazySingleton<AuthRepository>(
          () =>
              ApiAuthRepository(scope(), scope(), clientKind: readClientKind()),
        )
        ..registerFactory(() => RestoreSessionUseCase(scope()))
        ..registerFactory(() => SignInWithPasswordUseCase(scope()))
        ..registerFactory(() => SignUpWithPasswordUseCase(scope()))
        ..registerFactory(() => WatchAuthenticationStatusUseCase(scope()))
        ..registerFactory(() => ConfirmEmailVerificationUseCase(scope()))
        ..registerFactory(() => ResendEmailVerificationUseCase(scope()))
        ..registerLazySingleton(
          () => AuthSessionCubit(scope(), scope()),
          dispose: (cubit) => cubit.close(),
        )
        ..registerFactory(
          () => SignInFormCubit(
            scope(),
            scope<AuthSessionCubit>().setSignedInUser,
          ),
        )
        ..registerFactory(() => SignUpFormCubit(scope()))
        ..registerFactory(
          () => EmailVerificationCubit(
            scope(),
            scope(),
            scope<AuthSessionCubit>().setSignedInUser,
          ),
        ),
    );
  }
}
