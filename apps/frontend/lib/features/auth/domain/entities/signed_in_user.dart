import 'package:equatable/equatable.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/identity_provider.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';

/// Profile and sign-in capabilities of the current user.
final class const SignedInUser({
  /// Stable account identifier.
  required final String id,

  /// Current email address.
  required final EmailAddress email,

  /// Given name.
  required final String? firstName,

  /// Family name.
  required final String? lastName,

  /// Profile image URL, when known.
  required final String? avatarUrl,

  /// Preferred BCP 47 locale, when known.
  required final String? locale,

  /// Instance-level role.
  required final UserRole role,

  /// Whether password sign-in is available.
  required final bool hasPassword,

  /// Connected identity-provider names.
  required final List<IdentityProvider> linkedProviders,
}) extends Equatable {
  /// Creates the current user.
  this;

  @override
  List<Object?> get props => [
    id,
    email,
    firstName,
    lastName,
    avatarUrl,
    locale,
    role,
    hasPassword,
    linkedProviders,
  ];
}
