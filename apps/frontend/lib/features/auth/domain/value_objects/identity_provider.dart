/// External identity providers understood by this app version.
enum IdentityProvider(
  /// The provider name used by the API.
  final String wireName,
) {
  /// Google OpenID Connect.
  google('google');

  /// Decodes [wireName], or returns `null` for an unsupported provider.
  static IdentityProvider? tryFromWireName(String wireName) {
    for (final provider in IdentityProvider.values) {
      if (provider.wireName == wireName) return provider;
    }
    return null;
  }
}
