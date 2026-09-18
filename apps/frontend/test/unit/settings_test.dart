import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/settings.dart';

void main() {
  group('AppSettings.fromApiBaseUrl', () {
    test('accepts an absolute http URL as the API base URL', () {
      // Given: the backend's local development URL.
      const rawApiBaseUrl = 'http://localhost:8000';

      // When: the settings are built from it.
      final settings = AppSettings.fromApiBaseUrl(rawApiBaseUrl);

      // Then: the API base URL points at that backend.
      expect(settings.apiBaseUrl, Uri.parse('http://localhost:8000'));
    });

    test('rejects a URL without a scheme at startup', () {
      // Given: a host and port written without http or https.
      const rawApiBaseUrl = 'localhost:8000';

      // When: the settings are built from it.
      AppSettings build() => AppSettings.fromApiBaseUrl(rawApiBaseUrl);

      // Then: startup fails and names the setting.
      expect(
        build,
        throwsA(
          isA<ArgumentError>().having((e) => e.name, 'name', 'API_BASE_URL'),
        ),
      );
    });
  });
}
