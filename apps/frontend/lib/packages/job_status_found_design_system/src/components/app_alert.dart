import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// What kind of message an alert carries.
enum AppAlertVariant() {
  /// A message without a status, such as a tip.
  neutral,

  /// Something failed.
  error,

  /// Something the user may want to know.
  info,

  /// Something succeeded.
  success,

  /// Something may go wrong unless the user acts.
  warning,
}

/// An inline message that stays on the page, tinted by its [AppAlertVariant].
///
/// A screen reader announces the alert when it appears. Requires an ancestor
/// theme built by `AppTheme`.
class const AppAlert({
  /// The message, in one short sentence.
  required final String title,

  /// The line under [title] that explains the message or what to do, if any.
  final String? description,

  /// What kind of message the alert carries.
  final AppAlertVariant variant = AppAlertVariant.neutral,

  /// The icon before the text, in the color of [variant], if any.
  final IconData? icon,

  /// The widget at the trailing edge, such as a retry button, if any.
  final Widget? action,
  super.key,
}) extends StatelessWidget {
  /// Creates an alert.
  this;

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    final status = switch (variant) {
      AppAlertVariant.neutral => null,
      AppAlertVariant.error => colors.destructive,
      AppAlertVariant.info => colors.info,
      AppAlertVariant.success => colors.success,
      AppAlertVariant.warning => colors.warning,
    };

    return Semantics(
      container: true,
      liveRegion: true,
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md + AppSpacing.xxs,
          vertical: AppSpacing.md,
        ),
        decoration: BoxDecoration(
          color: status?.withValues(alpha: AppOpacity.tintSubtle),
          borderRadius: AppRadii.xl,
          border: Border.all(
            color:
                status?.withValues(alpha: AppOpacity.tintBorder) ??
                colors.border,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          spacing: AppSpacing.sm,
          children: [
            if (icon != null)
              Padding(
                // Centers the icon on the first text line.
                padding: const EdgeInsets.only(top: AppSpacing.xxs),
                child: Icon(
                  icon,
                  size: AppSizes.iconMd,
                  color: status ?? colors.mutedForeground,
                ),
              ),
            Expanded(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                spacing: AppSpacing.xxs,
                children: [
                  Text(
                    title,
                    style: AppTypography.sm.copyWith(
                      fontWeight: AppTypography.medium,
                      color: colors.cardForeground,
                    ),
                  ),
                  if (description case final description?)
                    Text(
                      description,
                      style: AppTypography.sm.copyWith(
                        color: colors.mutedForeground,
                      ),
                    ),
                ],
              ),
            ),
            ?action,
          ],
        ),
      ),
    );
  }
}
