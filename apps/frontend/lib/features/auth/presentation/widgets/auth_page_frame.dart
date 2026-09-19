import 'package:flutter/material.dart';
import 'package:job_status_found/features/localization/localization.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Shared wordmark, heading, subtitle, and centered auth-page column.
class const AuthPageFrame({
  required final String headline,
  required final Widget child,
  final String? subtitle,
  super.key,
}) extends StatelessWidget {
  /// Creates the shared auth-page content.
  this;

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings.of(context);
    final colors = AppColors.of(context);
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: AppSizes.formMaxWidth),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: AppSpacing.xl,
              children: [
                Text(
                  strings.appWordmark,
                  textAlign: TextAlign.center,
                  style: AppTypography.heading(AppTypography.xl)
                      .copyWith(color: colors.foreground),
                ),
                Column(
                  spacing: AppSpacing.sm,
                  children: [
                    Text(
                      headline,
                      textAlign: TextAlign.center,
                      style: AppTypography.heading(AppTypography.xxxl)
                          .copyWith(color: colors.foreground),
                    ),
                    Text(
                      subtitle ?? strings.auth.subtitle,
                      textAlign: TextAlign.center,
                      style: AppTypography.base.copyWith(
                        color: colors.mutedForeground,
                      ),
                    ),
                  ],
                ),
                child,
              ],
            ),
          ),
        ),
      ),
    );
  }
}
