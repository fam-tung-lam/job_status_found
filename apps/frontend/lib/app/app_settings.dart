/// Typed application configuration read at build time.
library;

/// Configuration the app needs before it starts.
final class const AppSettings._({
  /// The backend URL every API path is resolved against.
  required final Uri apiBaseUrl,
}) {
  /// Creates the configuration from an [apiBaseUrl] the factories already
  /// validated.
  this;

  /// Reads the configuration from `--dart-define` values.
  ///
  /// `API_BASE_URL` defaults to `http://localhost:8000`, where the backend's
  /// development server listens.
  ///
  /// Throws [ArgumentError] when `API_BASE_URL` is not an absolute `http` or
  /// `https` URL.
  factory fromEnvironment() => AppSettings.fromApiBaseUrl(
    const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000',
    ),
  );

  /// Builds the configuration from a raw backend base URL.
  ///
  /// Throws [ArgumentError] when [rawApiBaseUrl] is not an absolute `http` or
  /// `https` URL with a host.
  factory fromApiBaseUrl(String rawApiBaseUrl) {
    // Parse the raw value; a malformed URL parses to null.
    final url = Uri.tryParse(rawApiBaseUrl);

    // Refuse anything but an absolute http or https URL with a host, so a
    // wrong build define fails at start-up instead of on the first request.
    final isHttpUrl =
        url != null &&
        (url.isScheme('http') || url.isScheme('https')) &&
        url.host.isNotEmpty;
    if (!isHttpUrl) {
      throw ArgumentError.value(
        rawApiBaseUrl,
        'API_BASE_URL',
        'must be an absolute http or https URL, such as http://localhost:8000',
      );
    }

    return AppSettings._(apiBaseUrl: url);
  }
}
