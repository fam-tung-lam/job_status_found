/// The distances, in logical pixels, used for padding, margins, and gaps.
///
/// Every step sits on a 2-pixel grid, so neighboring widgets stay aligned.
abstract final class AppSpacing._() {
  /// Prevents instances; the class only holds spacing constants.
  this;

  /// 2 pixels: between a title and its supporting line.
  static const double xxs = 2;

  /// 4 pixels: between an icon and its label in a dense widget.
  static const double xs = 4;

  /// 8 pixels: between an icon and its label.
  static const double sm = 8;

  /// 12 pixels: inside a compact container.
  static const double md = 12;

  /// 16 pixels: between the parts of one group.
  static const double lg = 16;

  /// 24 pixels: inside a card, and between groups.
  static const double xl = 24;

  /// 32 pixels: between page sections.
  static const double xxl = 32;

  /// 48 pixels: around the content of a roomy, centered layout.
  static const double xxxl = 48;
}
