/// The opacities that derive one color from another.
abstract final class AppOpacity._() {
  /// Prevents instances; the class only holds opacity constants.
  this;

  /// A disabled control keeps 64% of its color.
  static const double disabled = 0.64;

  /// A filled control keeps 90% of its fill while hovered or pressed.
  static const double hoveredFill = 0.9;

  /// An icon beside a label keeps 80% of the label's color.
  static const double icon = 0.8;

  /// Placeholder text keeps 72% of the secondary text color.
  static const double placeholder = 0.72;

  /// 4%: the fill of a status alert.
  static const double tintSubtle = 0.04;

  /// 8%: the fill of a status badge on a light surface.
  static const double tint = 0.08;

  /// 16%: the fill of a status badge on a dark surface.
  static const double tintStrong = 0.16;

  /// 32%: the border of a status alert, and a control fill on a dark surface.
  static const double tintBorder = 0.32;
}
