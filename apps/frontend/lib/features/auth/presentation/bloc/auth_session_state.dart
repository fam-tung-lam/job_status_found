import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';

/// What the app knows about the current session.
sealed class const AuthSessionState() extends Equatable {
  /// Creates a session state.
  this;
  @override
  List<Object?> get props => const [];
}

/// Startup session restoration is still running.
final class const AuthSessionRestoring() extends AuthSessionState {
  /// Creates the state.
  this;
}

/// No usable session exists.
final class const AuthSessionSignedOut() extends AuthSessionState {
  /// Creates the state.
  this;
}

/// A session exists for [user].
final class const AuthSessionSignedIn(final SignedInUser user)
    extends AuthSessionState {
  /// Creates the state.
  this;
  @override
  List<Object?> get props => [user];
}
