import 'package:flutter/painting.dart';

/// The corner radii of every rounded shape.
abstract final class AppRadii._() {
  /// Prevents instances; the class only holds radius constants.
  this;

  /// 4 pixels: checkboxes and the smallest badge.
  static const xs = BorderRadius.all(Radius.circular(4));

  /// 6 pixels: badges, skeletons, and keyboard hints.
  static const sm = BorderRadius.all(Radius.circular(6));

  /// 8 pixels: the smallest buttons and icon tiles.
  static const md = BorderRadius.all(Radius.circular(8));

  /// 10 pixels: buttons, text fields, menus, and tooltips.
  static const lg = BorderRadius.all(Radius.circular(10));

  /// 14 pixels: alerts.
  static const xl = BorderRadius.all(Radius.circular(14));

  /// 16 pixels: cards and dialogs.
  static const xxl = BorderRadius.all(Radius.circular(16));

  /// A radius larger than any widget, which rounds the ends into a pill.
  static const full = BorderRadius.all(Radius.circular(999));
}
