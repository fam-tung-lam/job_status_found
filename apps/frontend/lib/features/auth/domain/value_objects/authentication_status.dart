/// Whether the auth boundary currently holds usable session credentials.
enum AuthenticationStatus() {
  /// Credential storage has not completed its initial read.
  initial,

  /// No session credentials are available.
  signedOut,

  /// Session credentials are available.
  signedIn,
}
