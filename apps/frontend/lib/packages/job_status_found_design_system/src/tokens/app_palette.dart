import 'dart:ui';

/// The raw colors that every semantic color is picked from.
///
/// Only `AppColors` reads the palette, so a widget follows the light and dark
/// theme instead of fixing one raw color. The solid steps match the Tailwind
/// palette; an alpha step is named after its opacity in percent.
abstract final class AppPalette._() {
  /// Prevents instances; the class only holds color constants.
  this;

  /// Pure white.
  static const white = Color(0xFFFFFFFF);

  /// Pure black.
  static const black = Color(0xFF000000);

  /// Black at 4% opacity: subtle fills on a light surface.
  static const blackAlpha4 = Color(0x0A000000);

  /// Black at 6% opacity: the sidebar hairline on a light surface.
  static const blackAlpha6 = Color(0x0F000000);

  /// Black at 8% opacity: hairline borders on a light surface.
  static const blackAlpha8 = Color(0x14000000);

  /// Black at 10% opacity: control borders on a light surface.
  static const blackAlpha10 = Color(0x1A000000);

  /// White at 4% opacity: subtle fills on a dark surface.
  static const whiteAlpha4 = Color(0x0AFFFFFF);

  /// White at 5% opacity: the sidebar hairline on a dark surface.
  static const whiteAlpha5 = Color(0x0DFFFFFF);

  /// White at 6% opacity: hairline borders on a dark surface.
  static const whiteAlpha6 = Color(0x0FFFFFFF);

  /// White at 8% opacity: control borders on a dark surface.
  static const whiteAlpha8 = Color(0x14FFFFFF);

  /// Neutral 50: the lightest gray.
  static const neutral50 = Color(0xFFFAFAFA);

  /// Neutral 100.
  static const neutral100 = Color(0xFFF5F5F5);

  /// Neutral 400.
  static const neutral400 = Color(0xFFA1A1A1);

  /// Neutral 500.
  static const neutral500 = Color(0xFF737373);

  /// Neutral 500 mixed with 10% black: secondary text on a light surface.
  static const neutral500Darkened = Color(0xFF686868);

  /// Neutral 500 mixed with 10% white: secondary text on a dark surface.
  static const neutral500Lightened = Color(0xFF818181);

  /// Neutral 800: the ink color on a light surface.
  static const neutral800 = Color(0xFF262626);

  /// Neutral 950 mixed with 3% white: the sidebar of the dark theme.
  static const neutral950Lifted3 = Color(0xFF111111);

  /// Neutral 950 mixed with 4% white: the background of the dark theme.
  static const neutral950Lifted4 = Color(0xFF141414);

  /// Neutral 950 mixed with 6% white: raised surfaces of the dark theme.
  static const neutral950Lifted6 = Color(0xFF191919);

  /// Neutral 800 at 64% over neutral 50: sidebar text on a light surface.
  static const neutral800Softened = Color(0xFF727272);

  /// Neutral 100 at 64% over the dark sidebar: sidebar text on a dark surface.
  static const neutral100Softened = Color(0xFFA3A3A3);

  /// Red 400.
  static const red400 = Color(0xFFFF6467);

  /// Red 500.
  static const red500 = Color(0xFFFB2C36);

  /// Red 500 mixed with 10% white: the destructive fill of the dark theme.
  static const red500Lightened = Color(0xFFFB414A);

  /// Red 700.
  static const red700 = Color(0xFFC10007);

  /// Blue 400.
  static const blue400 = Color(0xFF51A2FF);

  /// Blue 500.
  static const blue500 = Color(0xFF2B7FFF);

  /// Blue 700.
  static const blue700 = Color(0xFF1447E6);

  /// Emerald 400.
  static const emerald400 = Color(0xFF00D492);

  /// Emerald 500.
  static const emerald500 = Color(0xFF00BC7D);

  /// Emerald 700.
  static const emerald700 = Color(0xFF007A55);

  /// Amber 400.
  static const amber400 = Color(0xFFFFB900);

  /// Amber 500.
  static const amber500 = Color(0xFFFE9A00);

  /// Amber 700.
  static const amber700 = Color(0xFFBB4D00);
}
