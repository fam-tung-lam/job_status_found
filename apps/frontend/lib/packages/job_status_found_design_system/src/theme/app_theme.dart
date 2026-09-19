import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_color_scheme.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_text_theme.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/component_themes/app_button_style.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/component_themes/input_themes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/component_themes/selection_control_themes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/component_themes/surface_themes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// The Material themes of the app.
///
/// Give `MaterialApp` [light] as `theme` and [dark] as `darkTheme`. Each theme
/// carries its `AppColors` as a theme extension, which every design-system
/// component requires, and restyles the stock Material widgets to match.
abstract final class AppTheme._() {
  /// Prevents instances; the class only holds the two themes.
  this;

  /// The theme for a light surface.
  static final ThemeData light = _buildThemeData(
    AppColors.light,
    Brightness.light,
  );

  /// The theme for a dark surface.
  static final ThemeData dark = _buildThemeData(
    AppColors.dark,
    Brightness.dark,
  );

  /// Returns the theme that paints with [colors] at the given [brightness].
  static ThemeData _buildThemeData(AppColors colors, Brightness brightness) {
    ButtonStyle buttonStyle(AppButtonVariant variant) => buildAppButtonStyle(
      colors: colors,
      brightness: brightness,
      variant: variant,
    );

    return ThemeData(
      brightness: brightness,
      colorScheme: buildAppColorScheme(colors, brightness),
      extensions: [colors],
      fontFamily: AppTypography.fontFamily,
      fontFamilyFallback: AppTypography.fontFamilyFallback,
      textTheme: buildAppTextTheme(colors),
      scaffoldBackgroundColor: colors.background,
      canvasColor: colors.background,
      dividerColor: colors.border,
      focusColor: Colors.transparent,
      hoverColor: colors.accent,
      highlightColor: Colors.transparent,
      // Feedback comes from fill changes, never from an ink splash.
      splashFactory: NoSplash.splashFactory,
      iconTheme: IconThemeData(color: colors.foreground, size: AppSizes.iconMd),
      appBarTheme: buildAppAppBarTheme(colors),
      cardTheme: buildAppCardTheme(colors),
      checkboxTheme: buildAppCheckboxTheme(colors),
      dialogTheme: buildAppDialogTheme(colors),
      dividerTheme: buildAppDividerTheme(colors),
      filledButtonTheme: FilledButtonThemeData(
        style: buttonStyle(AppButtonVariant.primary),
      ),
      inputDecorationTheme: buildAppInputDecorationTheme(colors, brightness),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: buttonStyle(AppButtonVariant.outline),
      ),
      popupMenuTheme: buildAppPopupMenuTheme(colors),
      progressIndicatorTheme: buildAppProgressIndicatorTheme(colors),
      radioTheme: buildAppRadioTheme(colors),
      scrollbarTheme: buildAppScrollbarTheme(colors),
      snackBarTheme: buildAppSnackBarTheme(colors),
      switchTheme: buildAppSwitchTheme(colors),
      textButtonTheme: TextButtonThemeData(
        style: buttonStyle(AppButtonVariant.ghost),
      ),
      textSelectionTheme: buildAppTextSelectionTheme(colors),
      tooltipTheme: buildAppTooltipTheme(colors),
    );
  }
}
