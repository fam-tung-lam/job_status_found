import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_palette.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// What a badge says about the thing it labels.
enum AppBadgeVariant() {
  /// A solid primary fill, for the one badge that must stand out.
  primary,

  /// A translucent fill, for a neutral category or count.
  secondary,

  /// A bordered surface, for a quiet attribute.
  outline,

  /// A solid red fill, for a problem that needs action now.
  destructive,

  /// A red tint, for a failed or rejected state.
  error,

  /// A blue tint, for a neutral, informative state.
  info,

  /// A green tint, for a successful or accepted state.
  success,

  /// An amber tint, for a state that needs attention soon.
  warning,
}

/// How large a badge is.
enum AppBadgeSize() {
  /// 16 pixels tall, for a count beside an icon.
  sm,

  /// 18 pixels tall, the default.
  md,

  /// 22 pixels tall, for a badge beside a heading.
  lg,
}

/// A short, non-interactive label for a status, a category, or a count.
///
/// Requires an ancestor theme built by `AppTheme`.
class const AppBadge({
  /// The text on the badge; keep it to one or two words.
  required final String label,

  /// What the badge says about the thing it labels.
  final AppBadgeVariant variant = AppBadgeVariant.primary,

  /// How large the badge is.
  final AppBadgeSize size = AppBadgeSize.md,

  /// The icon before the label, if any.
  final IconData? icon,
  super.key,
}) extends StatelessWidget {
  /// Creates a badge.
  this;

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    Color tint(Color status) => status.withValues(
      alpha: isDark ? AppOpacity.tintStrong : AppOpacity.tint,
    );
    const clear = Colors.transparent;
    final (Color fill, Color foreground, Color border) = switch (variant) {
      AppBadgeVariant.primary => (
        colors.primary,
        colors.primaryForeground,
        clear,
      ),
      AppBadgeVariant.secondary => (
        colors.secondary,
        colors.secondaryForeground,
        clear,
      ),
      AppBadgeVariant.outline => (
        colors.background,
        colors.foreground,
        colors.input,
      ),
      AppBadgeVariant.destructive => (
        colors.destructive,
        AppPalette.white,
        clear,
      ),
      AppBadgeVariant.error => (
        tint(colors.destructive),
        colors.destructiveForeground,
        clear,
      ),
      AppBadgeVariant.info => (tint(colors.info), colors.infoForeground, clear),
      AppBadgeVariant.success => (
        tint(colors.success),
        colors.successForeground,
        clear,
      ),
      AppBadgeVariant.warning => (
        tint(colors.warning),
        colors.warningForeground,
        clear,
      ),
    };
    final (
      double height,
      double padding,
      TextStyle step,
      BorderRadius radius,
    ) = switch (size) {
      AppBadgeSize.sm => (16, 3, AppTypography.xxs, AppRadii.xs),
      AppBadgeSize.md => (18, 3, AppTypography.xs, AppRadii.sm),
      AppBadgeSize.lg => (22, 5, AppTypography.sm, AppRadii.sm),
    };

    return Container(
      height: height,
      constraints: BoxConstraints(minWidth: height),
      padding: EdgeInsets.symmetric(horizontal: padding),
      decoration: BoxDecoration(
        color: fill,
        borderRadius: radius,
        border: Border.all(color: border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        spacing: AppSpacing.xs,
        children: [
          if (icon != null)
            Icon(
              icon,
              size: AppSizes.iconXs,
              color: foreground.withValues(alpha: AppOpacity.icon),
            ),
          Text(
            label,
            maxLines: 1,
            // The badge height already fixes the line box.
            style: step.copyWith(
              height: 1,
              fontWeight: AppTypography.medium,
              color: foreground,
            ),
          ),
        ],
      ),
    );
  }
}
