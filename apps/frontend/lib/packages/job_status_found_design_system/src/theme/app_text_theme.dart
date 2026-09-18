import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// Returns the Material text theme that maps each Material text role to a
/// step of the type scale, colored with [colors].
///
/// Display, headline, and title roles are semibold headings. Body roles are
/// regular, and label roles are medium. The code below is the full mapping.
///
/// `bodyMedium` is the default text of the app. `bodySmall` takes the
/// secondary text color, because Material uses it for supporting lines.
TextTheme buildAppTextTheme(AppColors colors) {
  TextStyle heading(TextStyle step) =>
      AppTypography.heading(step).copyWith(color: colors.foreground);
  TextStyle body(TextStyle step, {Color? color}) => step.copyWith(
    fontWeight: AppTypography.regular,
    color: color ?? colors.foreground,
  );
  TextStyle label(TextStyle step) =>
      step.copyWith(fontWeight: AppTypography.medium, color: colors.foreground);

  return TextTheme(
    displayLarge: heading(AppTypography.xxxl),
    displayMedium: heading(AppTypography.xxxl),
    displaySmall: heading(AppTypography.xxl),
    headlineLarge: heading(AppTypography.xxl),
    headlineMedium: heading(AppTypography.xl),
    headlineSmall: heading(AppTypography.lg),
    titleLarge: heading(AppTypography.lg),
    titleMedium: heading(AppTypography.base),
    titleSmall: heading(AppTypography.sm),
    bodyLarge: body(AppTypography.base),
    bodyMedium: body(AppTypography.sm),
    bodySmall: body(AppTypography.xs, color: colors.mutedForeground),
    labelLarge: label(AppTypography.sm),
    labelMedium: label(AppTypography.xs),
    labelSmall: label(AppTypography.xxs),
  );
}
