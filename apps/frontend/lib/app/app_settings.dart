/// Typed application configuration read at build time.
library;

/// Configuration the app needs before it starts.
final class const AppSettings._({
  /// The backend URL every API path is resolved against.
  required final Uri apiBaseUrl,
  required final Uri termsUrl,
  required final Uri privacyUrl,
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
  factory fromEnvironment() {
    // Read every build-time setting before validating them together.
    const rawApiBaseUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000',
    );
    const rawTermsUrl = String.fromEnvironment(
      'TERMS_URL',
      defaultValue: 'https://example.com/terms',
    );
    const rawPrivacyUrl = String.fromEnvironment(
      'PRIVACY_URL',
      defaultValue: 'https://example.com/privacy',
    );

    return AppSettings.fromRawValues(
      rawApiBaseUrl,
      rawTermsUrl: rawTermsUrl,
      rawPrivacyUrl: rawPrivacyUrl,
    );
  }

  /// Builds the configuration from a raw backend base URL.
  ///
  /// Throws [ArgumentError] when [rawApiBaseUrl] is not an absolute `http` or
  /// `https` URL with a host.
  factory fromApiBaseUrl(String rawApiBaseUrl) => AppSettings.fromRawValues(
    rawApiBaseUrl,
    rawTermsUrl: 'https://example.com/terms',
    rawPrivacyUrl: 'https://example.com/privacy',
  );

  /// Builds configuration from all raw build-time values.
  factory fromRawValues(
    String rawApiBaseUrl, {
    required String rawTermsUrl,
    required String rawPrivacyUrl,
  }) {
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

    final termsUrl = _parsePublicUrl(rawTermsUrl, 'TERMS_URL');
    final privacyUrl = _parsePublicUrl(rawPrivacyUrl, 'PRIVACY_URL');
    return AppSettings._(
      apiBaseUrl: url,
      termsUrl: termsUrl,
      privacyUrl: privacyUrl,
    );
  }
}

/// Parses one absolute browser URL or rejects startup configuration.
Uri _parsePublicUrl(String rawUrl, String settingName) {
  final url = Uri.tryParse(rawUrl);
  if (url == null || !url.isScheme('https') || url.host.isEmpty) {
    throw ArgumentError.value(
      rawUrl,
      settingName,
      'must be an absolute https URL',
    );
  }
  return url;
}
