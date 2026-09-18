import 'package:flutter/animation.dart';

/// The durations and curves of every animation.
abstract final class AppMotion._() {
  /// Prevents instances; the class only holds motion constants.
  this;

  /// 150 milliseconds: press feedback and color changes.
  static const fast = Duration(milliseconds: 150);

  /// 200 milliseconds: a thumb, panel, or popup that moves.
  static const normal = Duration(milliseconds: 200);

  /// 2 seconds: one sweep of the skeleton highlight.
  static const skeletonSweep = Duration(seconds: 2);

  /// Starts fast and settles slowly; for anything that responds to the user.
  static const easeOut = Cubic(0.23, 1, 0.32, 1);

  /// Slow at both ends; for anything that moves across the screen.
  static const easeInOut = Cubic(0.77, 0, 0.175, 1);

  /// The scale of a button while it is pressed.
  static const double pressedScale = 0.97;
}
