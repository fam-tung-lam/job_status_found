/// Instance-level account roles understood by this app version.
enum UserRole(
  /// The role name used by the API.
  final String wireName,
) {
  /// An ordinary product user.
  user('user'),

  /// An administrator of the product instance.
  admin('admin');

  /// Decodes [wireName], or returns `null` for an unsupported role.
  static UserRole? tryFromWireName(String wireName) {
    for (final role in UserRole.values) {
      if (role.wireName == wireName) return role;
    }
    return null;
  }
}
