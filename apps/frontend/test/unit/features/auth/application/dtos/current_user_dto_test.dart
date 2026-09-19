import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/application/dtos/current_user_dto.dart';
import 'package:job_status_found/features/auth/domain/value_objects/identity_provider.dart';
import 'package:job_status_found/features/auth/domain/value_objects/user_role.dart';

void main() {
  group('CurrentUserDto.fromJson', () {
    test('decodes the profile and linked sign-in methods', () {
      // Given: the documented current-user response.
      final json = <String, Object?>{
        'id': '4f0a9441-0868-4c35-93f4-c38d195a2574',
        'email': 'person@example.com',
        'first_name': 'Pat',
        'last_name': 'Lee',
        'avatar_url': 'https://example.com/avatar.png',
        'locale': 'en-US',
        'role': 'user',
        'has_password': true,
        'linked_providers': <Object?>['google'],
      };

      // When: the app decodes and maps it.
      final user = CurrentUserDto.fromJson(json).toEntity();

      // Then: every session-relevant field survives the boundary.
      expect(user.email.asTyped, 'person@example.com');
      expect(user.firstName, 'Pat');
      expect(user.avatarUrl, 'https://example.com/avatar.png');
      expect(user.locale, 'en-US');
      expect(user.hasPassword, isTrue);
      expect(user.role, UserRole.user);
      expect(user.linkedProviders, [IdentityProvider.google]);
    });

    test('rejects a provider list with a non-string member', () {
      // Given: a malformed provider list.
      final json = <String, Object?>{
        'id': 'id',
        'email': 'person@example.com',
        'first_name': 'Pat',
        'last_name': 'Lee',
        'avatar_url': null,
        'locale': null,
        'role': 'user',
        'has_password': true,
        'linked_providers': <Object?>[1],
      };

      // When: the response is decoded.
      CurrentUserDto decode() => CurrentUserDto.fromJson(json);

      // Then: the invalid contract cannot enter session state.
      expect(decode, throwsFormatException);
    });
  });
}
