/// Client platforms supported by the auth API.
enum ClientKind(
  /// The request value accepted by the backend.
  final String wireName,
) {
  /// A browser using an HTTP-only refresh cookie.
  web('web'),

  /// An iOS app receiving its refresh token in the response body.
  ios('ios'),

  /// An Android app receiving its refresh token in the response body.
  android('android'),
}
