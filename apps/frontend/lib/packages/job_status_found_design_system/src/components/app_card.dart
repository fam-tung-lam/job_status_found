import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_shadows.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// A bordered surface that groups related content under an optional header
/// and above an optional footer.
///
/// The header appears when [title], [description], or [action] is given. The
/// card is as wide as its parent allows and as tall as its content. Requires
/// an ancestor theme built by `AppTheme`.
class const AppCard({
  /// The content of the card.
  required final Widget child,

  /// The heading of the card, if any.
  final String? title,

  /// The line under [title] that says what the card is for, if any.
  final String? description,

  /// The widget at the trailing edge of the header, such as a button, if any.
  final Widget? action,

  /// The widget under the content, such as a row of buttons, if any.
  final Widget? footer,
  super.key,
}) extends StatelessWidget {
  /// Creates a card.
  this;

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    final hasHeader = title != null || description != null || action != null;
    final hasFooter = footer != null;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: AppRadii.xxl,
        border: Border.all(color: colors.border),
        boxShadow: AppShadows.xs,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (hasHeader)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                AppSpacing.xl,
                AppSpacing.xl,
                AppSpacing.xl,
                AppSpacing.lg,
              ),
              child: _CardHeader(
                title: title,
                description: description,
                action: action,
              ),
            ),
          Padding(
            padding: EdgeInsets.fromLTRB(
              AppSpacing.xl,
              hasHeader ? 0 : AppSpacing.xl,
              AppSpacing.xl,
              hasFooter ? 0 : AppSpacing.xl,
            ),
            child: DefaultTextStyle.merge(
              style: TextStyle(color: colors.cardForeground),
              child: child,
            ),
          ),
          if (footer case final footer?)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                AppSpacing.xl,
                AppSpacing.lg,
                AppSpacing.xl,
                AppSpacing.xl,
              ),
              child: footer,
            ),
        ],
      ),
    );
  }
}

/// The title and description of a card, with its action at the trailing edge.
class const _CardHeader({
  /// The heading of the card, if any.
  required final String? title,

  /// The line under [title], if any.
  required final String? description,

  /// The widget at the trailing edge, if any.
  required final Widget? action,
}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      spacing: AppSpacing.lg,
      children: [
        Expanded(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            spacing: AppSpacing.xs + AppSpacing.xxs,
            children: [
              if (title case final title?)
                Text(
                  title,
                  style: AppTypography.heading(AppTypography.lg)
                      .copyWith(height: 1, color: colors.cardForeground),
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
    );
  }
}
