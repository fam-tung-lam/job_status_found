import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_palette.dart';

/// Returns the Material color scheme that gives stock Material widgets the
/// semantic [colors] of the theme with the given [brightness].
///
/// Material roles without a semantic counterpart take the closest one, so a
/// stock widget never falls back to a Material default color.
ColorScheme buildAppColorScheme(AppColors colors, Brightness brightness) {
  return ColorScheme(
    brightness: brightness,
    primary: colors.primary,
    onPrimary: colors.primaryForeground,
    primaryContainer: colors.secondary,
    onPrimaryContainer: colors.secondaryForeground,
    secondary: colors.primary,
    onSecondary: colors.primaryForeground,
    secondaryContainer: colors.secondary,
    onSecondaryContainer: colors.secondaryForeground,
    tertiary: colors.info,
    onTertiary: AppPalette.white,
    error: colors.destructive,
    onError: AppPalette.white,
    errorContainer: colors.destructive.withValues(alpha: AppOpacity.tint),
    onErrorContainer: colors.destructiveForeground,
    surface: colors.background,
    onSurface: colors.foreground,
    onSurfaceVariant: colors.mutedForeground,
    surfaceContainerLowest: colors.card,
    surfaceContainerLow: colors.card,
    surfaceContainer: colors.popover,
    surfaceContainerHigh: colors.popover,
    surfaceContainerHighest: colors.popover,
    outline: colors.input,
    outlineVariant: colors.border,
    inverseSurface: colors.primary,
    onInverseSurface: colors.primaryForeground,
    inversePrimary: colors.primaryForeground,
    shadow: AppPalette.black,
    scrim: AppPalette.black,
    // Depth comes from borders and shadows, never from a Material tint.
    surfaceTint: Colors.transparent,
  );
}
