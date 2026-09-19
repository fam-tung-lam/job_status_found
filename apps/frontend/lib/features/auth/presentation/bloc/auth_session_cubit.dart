import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:job_status_found/features/auth/application/use_cases/restore_session_use_case.dart';
import 'package:job_status_found/features/auth/application/use_cases/watch_authentication_status_use_case.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/failures/auth_failure.dart';
import 'package:job_status_found/features/auth/domain/value_objects/authentication_status.dart';
import 'package:job_status_found/features/auth/presentation/bloc/auth_session_state.dart';

/// Owns the app-wide signed-in or signed-out session state.
final class AuthSessionCubit(
  final RestoreSessionUseCase _restoreSession,
  WatchAuthenticationStatusUseCase watchAuthenticationStatus,
) extends Cubit<AuthSessionState> {
  /// Creates a restoring session cubit.
  this : super(const AuthSessionRestoring()) {
    _authenticationSubscription = watchAuthenticationStatus.invoke().listen(
      _handleAuthenticationStatus,
      onError: _handleAuthenticationFailure,
    );
  }

  /// Watches token revocation after the session has opened.
  late final StreamSubscription<AuthenticationStatus>
  _authenticationSubscription;

  /// Restores the session once at app startup.
  Future<void> restoreSession() async {
    try {
      final user = await _restoreSession.invoke();
      if (!isClosed) {
        emit(
          user == null
              ? const AuthSessionSignedOut()
              : AuthSessionSignedIn(user),
        );
      }
    } on AuthFailure {
      if (!isClosed) emit(const AuthSessionSignedOut());
    }
  }

  /// Publishes a newly opened session.
  void setSignedInUser(SignedInUser user) => emit(AuthSessionSignedIn(user));

  /// Returns to signed out when transparent refresh revokes tokens.
  void _handleAuthenticationStatus(AuthenticationStatus status) {
    if (status == AuthenticationStatus.signedOut &&
        state is AuthSessionSignedIn) {
      emit(const AuthSessionSignedOut());
    }
  }

  /// Falls back to signed out when credential observation fails at its domain
  /// boundary.
  void _handleAuthenticationFailure(Object error, StackTrace stackTrace) {
    if (error is AuthFailure) {
      if (!isClosed) emit(const AuthSessionSignedOut());
      return;
    }
    Zone.current.handleUncaughtError(error, stackTrace);
  }

  @override
  Future<void> close() async {
    await _authenticationSubscription.cancel();
    await super.close();
  }
}
