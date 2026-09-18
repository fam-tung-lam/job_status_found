import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// Returns the decoration of every text field: a compact, bordered box that
/// turns its border to the ring color on focus and to red on an error.
InputDecorationThemeData buildAppInputDecorationTheme(
  AppColors colors,
  Brightness brightness,
) {
  OutlineInputBorder border(Color color) => OutlineInputBorder(
    borderRadius: AppRadii.lg,
    borderSide: BorderSide(color: color),
  );
  final errorBorder = colors.destructive.withValues(
    alpha: AppOpacity.tintBorder,
  );

  return InputDecorationThemeData(
    isDense: true,
    filled: true,
    fillColor: brightness == Brightness.dark
        ? colors.input.withValues(alpha: colors.input.a * AppOpacity.tintBorder)
        : colors.background,
    hoverColor: Colors.transparent,
    contentPadding: const EdgeInsets.symmetric(
      horizontal: AppSpacing.md - AppSizes.hairline,
      vertical: AppSpacing.sm,
    ),
    hintStyle: AppTypography.sm.copyWith(
      color: colors.mutedForeground.withValues(alpha: AppOpacity.placeholder),
    ),
    labelStyle: AppTypography.sm.copyWith(color: colors.mutedForeground),
    floatingLabelStyle: AppTypography.sm.copyWith(color: colors.foreground),
    helperStyle: AppTypography.xs.copyWith(color: colors.mutedForeground),
    errorStyle: AppTypography.xs.copyWith(color: colors.destructiveForeground),
    prefixIconColor: colors.mutedForeground,
    suffixIconColor: colors.mutedForeground,
    border: border(colors.input),
    enabledBorder: border(colors.input),
    disabledBorder: border(
      colors.input.withValues(alpha: colors.input.a * AppOpacity.disabled),
    ),
    focusedBorder: border(colors.ring),
    errorBorder: border(errorBorder),
    focusedErrorBorder: border(colors.destructive),
  );
}

/// Returns the caret and selection colors of every text field.
TextSelectionThemeData buildAppTextSelectionTheme(AppColors colors) {
  return TextSelectionThemeData(
    cursorColor: colors.foreground,
    selectionColor: colors.ring.withValues(alpha: AppOpacity.tintBorder),
    selectionHandleColor: colors.foreground,
  );
}
