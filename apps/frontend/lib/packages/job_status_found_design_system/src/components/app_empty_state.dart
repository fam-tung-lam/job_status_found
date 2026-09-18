import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_shadows.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// A centered message for a view that has nothing to show yet, with an
/// optional next step.
///
/// Requires an ancestor theme built by `AppTheme`.
class const AppEmptyState({
  /// What is missing, in a few words.
  required final String title,

  /// The line under [title] that says why, or what to do next, if any.
  final String? description,

  /// The icon above the text, drawn on a small stack of tiles, if any.
  final IconData? icon,

  /// The widget under the text that starts the next step, such as a button,
  /// if any.
  final Widget? action,
  super.key,
}) extends StatelessWidget {
  /// Creates an empty state.
  this;

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: AppSizes.proseMaxWidth),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon case final icon?) ...[
              _IconTileStack(icon),
              const SizedBox(height: AppSpacing.xl),
            ],
            Text(
              title,
              textAlign: TextAlign.center,
              style: AppTypography.heading(AppTypography.xl)
                  .copyWith(color: colors.foreground),
            ),
            if (description case final description?) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                description,
                textAlign: TextAlign.center,
                style: AppTypography.sm.copyWith(color: colors.mutedForeground),
              ),
            ],
            if (action case final action?) ...[
              const SizedBox(height: AppSpacing.xl),
              action,
            ],
          ],
        ),
      ),
    );
  }
}

/// An icon on a raised tile, with two empty tiles fanned out behind it.
class const _IconTileStack(
  /// The icon on the front tile.
  final IconData icon,
) extends StatelessWidget {
  /// The side length of each tile.
  static const double _tileSize = AppSizes.controlLg;

  /// How far each back tile leans away from the front tile, in radians; ten
  /// degrees.
  static const double _lean = 0.1745;

  /// The scale of each back tile relative to the front tile.
  static const double _backTileScale = 0.84;

  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Transform(
          alignment: Alignment.bottomLeft,
          transform: Matrix4.rotationZ(-_lean)
            ..scaleByDouble(_backTileScale, _backTileScale, 1, 1),
          child: const _Tile(),
        ),
        Transform(
          alignment: Alignment.bottomRight,
          transform: Matrix4.rotationZ(_lean)
            ..scaleByDouble(_backTileScale, _backTileScale, 1, 1),
          child: const _Tile(),
        ),
        _Tile(icon: icon),
      ],
    );
  }
}

/// A small bordered square; the front one is raised and holds the icon.
class const _Tile({
  /// The icon in the middle; an empty back tile when `null`.
  final IconData? icon,
}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    return Container(
      width: _IconTileStack._tileSize,
      height: _IconTileStack._tileSize,
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: AppRadii.md,
        border: Border.all(color: colors.border),
        boxShadow: icon == null ? null : AppShadows.sm,
      ),
      child: icon == null
          ? null
          : Icon(icon, size: AppSizes.iconLg, color: colors.foreground),
    );
  }
}
