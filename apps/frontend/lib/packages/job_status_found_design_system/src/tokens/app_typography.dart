import 'package:flutter/painting.dart';

/// The typeface, weights, and type scale.
///
/// A scale step fixes the size and line height only. The reader of a step adds
/// the weight and the color, which comes from `AppColors`.
abstract final class AppTypography._() {
  /// Prevents instances; the class only holds typography constants.
  this;

  /// The bundled typeface, declared under `fonts:` in the app's
  /// `pubspec.yaml`.
  static const fontFamily = 'Geist';

  /// The typefaces tried, in order, for a glyph that [fontFamily] lacks.
  static const fontFamilyFallback = ['system-ui', 'sans-serif'];

  /// Body text.
  static const FontWeight regular = FontWeight.w400;

  /// Labels, buttons, and badges.
  static const FontWeight medium = FontWeight.w500;

  /// Headings and titles.
  static const FontWeight semibold = FontWeight.w600;

  /// The letter spacing of a heading, as a fraction of its font size.
  static const double headingTracking = -0.025;

  /// 10 pixels on a 16-pixel line: the smallest badge.
  static const xxs = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 10,
    height: 16 / 10,
  );

  /// 12 pixels on a 16-pixel line: captions, badges, and keyboard hints.
  static const xs = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 12,
    height: 16 / 12,
  );

  /// 14 pixels on a 20-pixel line: the default text of the app.
  static const sm = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 14,
    height: 20 / 14,
  );

  /// 16 pixels on a 24-pixel line: text fields and roomy body text.
  static const base = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 16,
    height: 24 / 16,
  );

  /// 18 pixels on a 28-pixel line: card titles.
  static const lg = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 18,
    height: 28 / 18,
  );

  /// 20 pixels on a 28-pixel line: section headings.
  static const xl = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 20,
    height: 28 / 20,
  );

  /// 24 pixels on a 32-pixel line: page headings.
  static const xxl = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 24,
    height: 32 / 24,
  );

  /// 30 pixels on a 36-pixel line: the largest heading.
  static const xxxl = TextStyle(
    fontFamily: fontFamily,
    fontFamilyFallback: fontFamilyFallback,
    fontSize: 30,
    height: 36 / 30,
  );

  /// Returns [step] as a heading: semibold, with tightened letter spacing.
  static TextStyle heading(TextStyle step) => step.copyWith(
    fontWeight: semibold,
    letterSpacing: (step.fontSize ?? sm.fontSize!) * headingTracking,
  );
}
