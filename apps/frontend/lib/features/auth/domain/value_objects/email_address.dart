import 'package:equatable/equatable.dart';

/// A syntactically valid email address ready for an auth operation.
final class const EmailAddress._(
  /// The address as entered, with surrounding whitespace removed.
  final String asTyped,
) extends Equatable {
  /// Creates a validated address from its trimmed text.
  this;

  /// Parses [text], or returns `null` when it is not valid email syntax.
  static EmailAddress? tryParse(String text) {
    final trimmedText = text.trim();
    if (trimmedText.length > 254 || !_emailSyntax.hasMatch(trimmedText)) {
      return null;
    }
    final separatorIndex = trimmedText.lastIndexOf('@');
    if (separatorIndex > 64) return null;
    return EmailAddress._(trimmedText);
  }

  /// The deliberately conservative syntax accepted before server validation.
  static final RegExp _emailSyntax = RegExp(
    r'^[^\s@.]+(?:\.[^\s@.]+)*@[^\s@.-]+(?:[^\s@.]*[^\s@.-])?(?:\.[^\s@.-]+(?:[^\s@.]*[^\s@.-])?)+$',
  );

  @override
  List<Object?> get props => [asTyped];

  @override
  String toString() => asTyped;
}
