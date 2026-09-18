import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// Returns the look of every app bar: flat, in the page color, with a
/// hairline below it that stays the same while content scrolls under.
AppBarThemeData buildAppAppBarTheme(AppColors colors) {
  return AppBarThemeData(
    backgroundColor: colors.background,
    foregroundColor: colors.foreground,
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    scrolledUnderElevation: 0,
    centerTitle: false,
    titleSpacing: AppSpacing.lg,
    titleTextStyle: AppTypography.heading(AppTypography.base)
        .copyWith(color: colors.foreground),
    shape: Border(bottom: BorderSide(color: colors.border)),
  );
}

/// Returns the look of every stock Material card: flat and bordered, the same
/// surface `AppCard` draws.
CardThemeData buildAppCardTheme(AppColors colors) {
  return CardThemeData(
    color: colors.card,
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    margin: EdgeInsets.zero,
    shape: RoundedRectangleBorder(
      borderRadius: AppRadii.xxl,
      side: BorderSide(color: colors.border),
    ),
  );
}

/// Returns the look of every dialog: a bordered popover surface.
DialogThemeData buildAppDialogTheme(AppColors colors) {
  return DialogThemeData(
    backgroundColor: colors.popover,
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    shape: RoundedRectangleBorder(
      borderRadius: AppRadii.xxl,
      side: BorderSide(color: colors.border),
    ),
    titleTextStyle: AppTypography.heading(AppTypography.lg)
        .copyWith(color: colors.popoverForeground),
    contentTextStyle: AppTypography.sm.copyWith(color: colors.mutedForeground),
  );
}

/// Returns the look of every divider: a hairline that takes no extra space.
DividerThemeData buildAppDividerTheme(AppColors colors) {
  return DividerThemeData(
    color: colors.border,
    thickness: AppSizes.hairline,
    space: AppSizes.hairline,
  );
}

/// Returns the look of every popup menu: a bordered popover surface.
PopupMenuThemeData buildAppPopupMenuTheme(AppColors colors) {
  return PopupMenuThemeData(
    color: colors.popover,
    surfaceTintColor: Colors.transparent,
    elevation: 0,
    shape: RoundedRectangleBorder(
      borderRadius: AppRadii.lg,
      side: BorderSide(color: colors.border),
    ),
    textStyle: AppTypography.sm.copyWith(color: colors.popoverForeground),
  );
}

/// Returns the look of every tooltip: a small bordered popover surface.
TooltipThemeData buildAppTooltipTheme(AppColors colors) {
  return TooltipThemeData(
    decoration: BoxDecoration(
      color: colors.popover,
      borderRadius: AppRadii.md,
      border: Border.all(color: colors.border),
    ),
    padding: const EdgeInsets.symmetric(
      horizontal: AppSpacing.sm,
      vertical: AppSpacing.xs,
    ),
    textStyle: AppTypography.xs.copyWith(color: colors.popoverForeground),
  );
}

/// Returns the look of every snack bar: a floating bar in the primary color.
SnackBarThemeData buildAppSnackBarTheme(AppColors colors) {
  return SnackBarThemeData(
    behavior: SnackBarBehavior.floating,
    backgroundColor: colors.primary,
    contentTextStyle: AppTypography.sm.copyWith(
      color: colors.primaryForeground,
    ),
    actionTextColor: colors.primaryForeground,
    elevation: 0,
    shape: const RoundedRectangleBorder(borderRadius: AppRadii.lg),
  );
}

/// Returns the look of every progress indicator: a thin stroke in the
/// secondary text color over a quiet track.
ProgressIndicatorThemeData buildAppProgressIndicatorTheme(AppColors colors) {
  return ProgressIndicatorThemeData(
    color: colors.mutedForeground,
    linearTrackColor: colors.muted,
    circularTrackColor: Colors.transparent,
    strokeWidth: AppSizes.focusRing,
    strokeCap: StrokeCap.round,
  );
}

/// Returns the look of every scrollbar: a thin thumb in the border color.
ScrollbarThemeData buildAppScrollbarTheme(AppColors colors) {
  return ScrollbarThemeData(
    thickness: const WidgetStatePropertyAll(AppSpacing.sm),
    radius: AppRadii.full.topLeft,
    thumbColor: WidgetStatePropertyAll(colors.border),
  );
}
