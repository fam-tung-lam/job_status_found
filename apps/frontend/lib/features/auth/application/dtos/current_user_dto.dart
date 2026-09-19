import 'package:job_status_found/features/auth/domain/entities/signed_in_user.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';
import 'package:job_status_found/features/auth/domain/value_objects/identity_provider.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';

/// Current-user response from `GET /v1/auth/me`.
final class const CurrentUserDto({
  /// Account identifier.
  required final String id,

  /// Email address.
  required final EmailAddress email,

  /// Given name.
  required final String? firstName,

  /// Family name.
  required final String? lastName,

  /// Profile image URL, when known.
  required final String? avatarUrl,

  /// Preferred BCP 47 locale, when known.
  required final String? locale,

  /// Instance role.
  required final UserRole role,

  /// Whether a password is set.
  required final bool hasPassword,

  /// Connected provider names.
  required final List<IdentityProvider> linkedProviders,
}) {
  /// Creates a current-user DTO.
  this;

  /// Decodes the documented response.
  factory fromJson(Map<String, Object?> json) {
    final providers = json['linked_providers'];
    if (json
        case {
          'id': final String id,
          'email': final String email,
          'first_name': final String? firstName,
          'last_name': final String? lastName,
          'avatar_url': final String? avatarUrl,
          'locale': final String? locale,
          'role': final String role,
          'has_password': final bool hasPassword,
        }
        when providers is List<Object?> &&
            providers.every((provider) => provider is String)) {
      final parsedEmail = EmailAddress.tryParse(email);
      final parsedRole = UserRole.tryFromWireName(role);
      final parsedProviders = providers
          .cast<String>()
          .map(IdentityProvider.tryFromWireName)
          .toList();
      if (parsedEmail == null ||
          parsedRole == null ||
          parsedProviders.any((provider) => provider == null)) {
        throw const FormatException('Invalid current-user response.');
      }
      return CurrentUserDto(
        id: id,
        email: parsedEmail,
        firstName: firstName,
        lastName: lastName,
        avatarUrl: avatarUrl,
        locale: locale,
        role: parsedRole,
        hasPassword: hasPassword,
        linkedProviders: parsedProviders.cast<IdentityProvider>(),
      );
    }
    throw const FormatException('Invalid current-user response.');
  }

  /// Converts the wire response to the domain entity.
  SignedInUser toEntity() => SignedInUser(
    id: id,
    email: email,
    firstName: firstName,
    lastName: lastName,
    avatarUrl: avatarUrl,
    locale: locale,
    role: role,
    hasPassword: hasPassword,
    linkedProviders: linkedProviders,
  );
}
