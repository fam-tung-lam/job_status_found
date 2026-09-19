/// The fixed dimensions, in logical pixels, of controls, icons, and borders.
abstract final class AppSizes._() {
  /// Prevents instances; the class only holds size constants.
  this;

  /// 24 pixels: the height of an extra-small control.
  static const double controlXs = 24;

  /// 28 pixels: the height of a small control.
  static const double controlSm = 28;

  /// 32 pixels: the height of a default control.
  static const double controlMd = 32;

  /// 36 pixels: the height of a large control.
  static const double controlLg = 36;

  /// 40 pixels: the height of an extra-large control.
  static const double controlXl = 40;

  /// 48 pixels: a roomy control and the minimum touch target.
  static const double controlXxl = 48;

  /// 12 pixels: an icon inside a badge.
  static const double iconXs = 12;

  /// 14 pixels: an icon inside an extra-small control.
  static const double iconSm = 14;

  /// 16 pixels: the default icon.
  static const double iconMd = 16;

  /// 18 pixels: an icon inside an extra-large control or an icon tile.
  static const double iconLg = 18;

  /// 1 pixel: every border and divider.
  static const double hairline = 1;

  /// 2 pixels: the ring around a widget that has keyboard focus.
  static const double focusRing = 2;

  /// 384 pixels: the widest a centered block of text grows.
  static const double proseMaxWidth = 384;

  /// 400 pixels: the widest an authentication form grows.
  static const double formMaxWidth = 400;
}
