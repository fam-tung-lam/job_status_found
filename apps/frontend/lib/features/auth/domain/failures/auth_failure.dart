import 'package:job_status_found/features/auth/domain/value_objects/auth_rejection_code.dart';

/// An auth operation rejected by the server or unable to reach it.
sealed class const AuthFailure() implements Exception {
  /// Creates an auth failure.
  this;
}

/// The backend rejected the operation for a stable [code].
final class const AuthRejectedFailure(
  final AuthRejectionCode code, {
  final int? retryAfterSeconds,
}) extends AuthFailure {
  /// Creates a rejection.
  this;
}

/// The backend could not be reached or returned an unusable response.
final class const AuthServerUnreachableFailure() extends AuthFailure {
  /// Creates the connectivity failure.
  this;
}
