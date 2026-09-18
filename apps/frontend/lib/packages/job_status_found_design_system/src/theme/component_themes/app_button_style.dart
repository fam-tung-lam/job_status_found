import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_motion.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_palette.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// How much a button stands out, and what its action means.
enum AppButtonVariant() {
  /// A solid fill, for the main action of a view.
  primary,

  /// A translucent fill, for an action beside the main one.
  secondary,

  /// A bordered surface, for a neutral action such as cancel.
  outline,

  /// No fill until hovered, for an action inside a toolbar or a row.
  ghost,

  /// Text that underlines while hovered, for an action inside a sentence.
  link,

  /// A solid red fill, for an action that deletes or cannot be undone.
  destructive,

  /// A bordered surface with red text, for a destructive action that is not
  /// the main action of its view.
  destructiveOutline,
}

/// How tall a button is, which also sets its padding, text, and icon size.
enum AppButtonSize() {
  /// 24 pixels tall, for a dense table row or a tag editor.
  xs,

  /// 28 pixels tall, for a toolbar.
  sm,

  /// 32 pixels tall, the default.
  md,

  /// 36 pixels tall, for a form's submit action.
  lg,

  /// 40 pixels tall, for the single action of a page.
  xl,
}

/// The dimensions that one [AppButtonSize] fixes.
final class const _ButtonMetrics({
  /// The height of the button, and its minimum width.
  required final double height,

  /// The space between the border and the content, left and right.
  required final double horizontalPadding,

  /// The scale step of the label.
  required final TextStyle labelStep,

  /// The size of an icon beside the label.
  required final double iconSize,

  /// The corner radius of the button.
  required final BorderRadius radius,
}) {
  /// Returns the dimensions of [size].
  ///
  /// The padding is one pixel short of the spacing grid, because the border
  /// takes that pixel.
  factory of(AppButtonSize size) => switch (size) {
    AppButtonSize.xs => const _ButtonMetrics(
      height: AppSizes.controlXs,
      horizontalPadding: 7,
      labelStep: AppTypography.xs,
      iconSize: AppSizes.iconSm,
      radius: AppRadii.md,
    ),
    AppButtonSize.sm => const _ButtonMetrics(
      height: AppSizes.controlSm,
      horizontalPadding: 9,
      labelStep: AppTypography.sm,
      iconSize: AppSizes.iconMd,
      radius: AppRadii.lg,
    ),
    AppButtonSize.md => const _ButtonMetrics(
      height: AppSizes.controlMd,
      horizontalPadding: 11,
      labelStep: AppTypography.sm,
      iconSize: AppSizes.iconMd,
      radius: AppRadii.lg,
    ),
    AppButtonSize.lg => const _ButtonMetrics(
      height: AppSizes.controlLg,
      horizontalPadding: 13,
      labelStep: AppTypography.sm,
      iconSize: AppSizes.iconMd,
      radius: AppRadii.lg,
    ),
    AppButtonSize.xl => const _ButtonMetrics(
      height: AppSizes.controlXl,
      horizontalPadding: 15,
      labelStep: AppTypography.base,
      iconSize: AppSizes.iconLg,
      radius: AppRadii.lg,
    ),
  };
}

/// The colors that one [AppButtonVariant] fixes.
final class const _ButtonPaint({
  /// The fill at rest.
  required final Color fill,

  /// The fill while hovered or pressed.
  required final Color activeFill,

  /// The color of the label and icon.
  required final Color foreground,

  /// The border at rest.
  required final Color border,

  /// The border while hovered or pressed; the same as [border] by default.
  final Color? activeBorder,
}) {
  /// Returns the colors of [variant] in the theme with the given
  /// [brightness].
  factory of(
    AppButtonVariant variant,
    AppColors colors,
    Brightness brightness,
  ) {
    const clear = Colors.transparent;
    final isDark = brightness == Brightness.dark;
    // A bordered button sits on the popover surface in the light theme, and
    // on a translucent control fill in the dark theme.
    final borderedFill = isDark
        ? colors.input.withValues(alpha: colors.input.a * AppOpacity.tintBorder)
        : colors.popover;
    return switch (variant) {
      AppButtonVariant.primary => _ButtonPaint(
        fill: colors.primary,
        activeFill: colors.primary.withValues(alpha: AppOpacity.hoveredFill),
        foreground: colors.primaryForeground,
        border: clear,
      ),
      AppButtonVariant.secondary => _ButtonPaint(
        fill: colors.secondary,
        activeFill: colors.secondary.withValues(alpha: colors.secondary.a * 2),
        foreground: colors.secondaryForeground,
        border: clear,
      ),
      AppButtonVariant.outline => _ButtonPaint(
        fill: borderedFill,
        activeFill: Color.alphaBlend(colors.accent, borderedFill),
        foreground: colors.foreground,
        border: colors.input,
      ),
      AppButtonVariant.ghost => _ButtonPaint(
        fill: clear,
        activeFill: colors.accent,
        foreground: colors.foreground,
        border: clear,
      ),
      AppButtonVariant.link => _ButtonPaint(
        fill: clear,
        activeFill: clear,
        foreground: colors.foreground,
        border: clear,
      ),
      AppButtonVariant.destructive => _ButtonPaint(
        fill: colors.destructive,
        activeFill: colors.destructive.withValues(
          alpha: AppOpacity.hoveredFill,
        ),
        foreground: AppPalette.white,
        border: clear,
      ),
      AppButtonVariant.destructiveOutline => _ButtonPaint(
        fill: borderedFill,
        activeFill: Color.alphaBlend(
          colors.destructive.withValues(alpha: AppOpacity.tintSubtle),
          borderedFill,
        ),
        foreground: colors.destructiveForeground,
        border: colors.input,
        activeBorder: colors.destructive.withValues(
          alpha: AppOpacity.tintBorder,
        ),
      ),
    };
  }
}

/// Whether [states] say the pointer is over the button or holding it down.
bool _isActive(Set<WidgetState> states) =>
    states.contains(WidgetState.hovered) ||
    states.contains(WidgetState.pressed);

/// Returns the Material button style of a button with the given [variant] and
/// [size], painted with [colors] in the theme with the given [brightness].
///
/// `AppButton` applies the style to its own button, and `AppTheme` applies it
/// to the stock Material buttons, so both look the same. Feedback comes from a
/// fill change instead of an ink splash. A disabled button keeps its colors at
/// a lower opacity, and a button with keyboard focus gains a ring.
ButtonStyle buildAppButtonStyle({
  required AppColors colors,
  required Brightness brightness,
  AppButtonVariant variant = AppButtonVariant.primary,
  AppButtonSize size = AppButtonSize.md,
}) {
  final metrics = _ButtonMetrics.of(size);
  final paint = _ButtonPaint.of(variant, colors, brightness);

  Color dimmedWhenDisabled(Color color, Set<WidgetState> states) =>
      states.contains(WidgetState.disabled)
      ? color.withValues(alpha: color.a * AppOpacity.disabled)
      : color;

  return ButtonStyle(
    textStyle: WidgetStateProperty.resolveWith(
      (states) => metrics.labelStep.copyWith(
        fontWeight: AppTypography.medium,
        decoration: variant == AppButtonVariant.link && _isActive(states)
            ? TextDecoration.underline
            : TextDecoration.none,
      ),
    ),
    foregroundColor: WidgetStateProperty.resolveWith(
      (states) => dimmedWhenDisabled(paint.foreground, states),
    ),
    iconColor: WidgetStateProperty.resolveWith(
      (states) => dimmedWhenDisabled(
        paint.foreground.withValues(alpha: AppOpacity.icon),
        states,
      ),
    ),
    iconSize: WidgetStatePropertyAll(metrics.iconSize),
    backgroundColor: WidgetStateProperty.resolveWith(
      (states) => dimmedWhenDisabled(
        _isActive(states) ? paint.activeFill : paint.fill,
        states,
      ),
    ),
    // The fill change above replaces the Material hover and press overlay.
    overlayColor: const WidgetStatePropertyAll(Colors.transparent),
    splashFactory: NoSplash.splashFactory,
    shadowColor: const WidgetStatePropertyAll(Colors.transparent),
    surfaceTintColor: const WidgetStatePropertyAll(Colors.transparent),
    elevation: const WidgetStatePropertyAll(0),
    side: WidgetStateProperty.resolveWith((states) {
      if (states.contains(WidgetState.focused)) {
        return BorderSide(
          color: colors.ring,
          width: AppSizes.focusRing,
          strokeAlign: BorderSide.strokeAlignOutside,
        );
      }
      final border = _isActive(states)
          ? paint.activeBorder ?? paint.border
          : paint.border;
      return BorderSide(color: dimmedWhenDisabled(border, states));
    }),
    shape: WidgetStatePropertyAll(
      RoundedRectangleBorder(borderRadius: metrics.radius),
    ),
    padding: WidgetStatePropertyAll(
      EdgeInsets.symmetric(horizontal: metrics.horizontalPadding),
    ),
    minimumSize: WidgetStatePropertyAll(Size.square(metrics.height)),
    // Material shrinks a button on desktop by default, which would break the
    // heights of the size scale.
    visualDensity: VisualDensity.standard,
    mouseCursor: WidgetStateProperty.resolveWith(
      (states) => states.contains(WidgetState.disabled)
          ? SystemMouseCursors.basic
          : SystemMouseCursors.click,
    ),
    animationDuration: AppMotion.fast,
    alignment: Alignment.center,
  );
}
