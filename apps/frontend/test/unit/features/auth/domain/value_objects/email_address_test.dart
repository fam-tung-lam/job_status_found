import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/auth/domain/value_objects/email_address.dart';

void main() {
  group('EmailAddress.tryParse', () {
    test('trims a syntactically valid address once at the boundary', () {
      // Given: an address with harmless surrounding whitespace.
      const text = '  person@example.com  ';

      // When: the form parses the address.
      final email = EmailAddress.tryParse(text);

      // Then: the domain value retains only the address.
      expect(email?.asTyped, 'person@example.com');
    });

    for (final text in [
      '',
      'person',
      'person@example',
      '.person@example.com',
      'person..name@example.com',
      'person@-example.com',
      'person@example-.com',
    ]) {
      test('rejects invalid syntax: $text', () {
        // Given: text that does not identify a valid mailbox.

        // When: the form parses the text.
        final email = EmailAddress.tryParse(text);

        // Then: no domain email can be created.
        expect(email, isNull);
      });
    }
  });
}
