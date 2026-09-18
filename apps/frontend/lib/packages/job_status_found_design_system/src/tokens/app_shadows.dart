import 'package:flutter/painting.dart';

/// The shadows that lift a surface off the one below it.
///
/// Surfaces are separated by hairline borders first; a shadow only adds a hint
/// of depth, so both themes share the same values.
abstract final class AppShadows._() {
  /// Prevents instances; the class only holds shadow constants.
  this;

  /// Barely visible: cards, outlined buttons, and text fields.
  static const xs = [
    BoxShadow(color: Color(0x0D000000), offset: Offset(0, 1), blurRadius: 2),
  ];

  /// Soft: small raised tiles.
  static const sm = [
    BoxShadow(color: Color(0x1A000000), offset: Offset(0, 1), blurRadius: 3),
    BoxShadow(
      color: Color(0x1A000000),
      offset: Offset(0, 1),
      blurRadius: 2,
      spreadRadius: -1,
    ),
  ];

  /// Pronounced: menus, popovers, and dialogs that float above the page.
  static const lg = [
    BoxShadow(
      color: Color(0x1A000000),
      offset: Offset(0, 10),
      blurRadius: 15,
      spreadRadius: -3,
    ),
    BoxShadow(
      color: Color(0x1A000000),
      offset: Offset(0, 4),
      blurRadius: 6,
      spreadRadius: -4,
    ),
  ];
}
