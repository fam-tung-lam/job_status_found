/// Tokens issued for one authenticated session.
final class const JobStatusFoundAuthTokens({
  /// Short-lived bearer token.
  required final String accessToken,

  /// Rotating refresh token, absent for web cookie sessions.
  required final String? refreshToken,

  /// Access-token lifetime in seconds.
  required final int expiresIn,

  /// Authorization scheme returned by the API.
  required final JobStatusFoundAuthTokenType tokenType,

  /// When this token set was received.
  required final DateTime issuedAt,
}) {
  /// Creates one token set.
  this;
}

/// OAuth token types understood by the HTTP client.
enum JobStatusFoundAuthTokenType(
  /// The OAuth response and header value.
  final String wireName,
) {
  /// A bearer token sent through the HTTP `Authorization` header.
  bearer('Bearer');

  /// Decodes [wireName], or returns `null` for an unsupported token type.
  static JobStatusFoundAuthTokenType? tryFromWireName(String wireName) {
    for (final tokenType in JobStatusFoundAuthTokenType.values) {
      if (tokenType.wireName.toLowerCase() == wireName.toLowerCase()) {
        return tokenType;
      }
    }
    return null;
  }
}

/// Whether the HTTP client currently holds authentication tokens.
enum JobStatusFoundAuthenticationStatus() {
  /// Token storage has not completed its initial read.
  initial,

  /// No authentication tokens are available.
  signedOut,

  /// Authentication tokens are available.
  signedIn,
}

/// HTTP access to the job_status_found API.
abstract interface class JobStatusFoundHttpClient() {
  /// Creates the client.
  this;

  /// Sends `GET` and returns its decoded JSON body.
  Future<Object?> get(
    String path, {
    Map<String, Object?> queryParameters = const {},
  });

  /// Sends `POST` with an optional JSON [body].
  Future<Object?> post(String path, {Object? body});

  /// Sends `PUT` with an optional JSON [body].
  Future<Object?> put(String path, {Object? body});

  /// Sends `DELETE` with an optional JSON [body].
  Future<Object?> delete(String path, {Object? body});

  /// Stores [tokens] and starts attaching their access token.
  Future<void> setTokens(JobStatusFoundAuthTokens tokens);

  /// Deletes the current tokens and stops attaching authentication.
  Future<void> clearTokens();

  /// Emits whenever the presence of authentication tokens changes.
  Stream<JobStatusFoundAuthenticationStatus> get authenticationStatus;

  /// Releases the connections this client holds.
  void close();
}
