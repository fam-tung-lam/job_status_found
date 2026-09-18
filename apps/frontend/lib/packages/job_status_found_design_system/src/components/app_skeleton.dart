import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_motion.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_palette.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';

/// A quiet placeholder in the shape of content that is still loading.
///
/// A highlight sweeps across the placeholder, unless the platform asks for
/// reduced motion. Requires an ancestor theme built by `AppTheme`.
class const AppSkeleton({
  /// The width of the placeholder; as wide as the parent allows when `null`.
  final double? width,

  /// The height of the placeholder; as tall as the parent allows when `null`.
  final double? height,

  /// The corner radius; use `AppRadii.full` for a line of text or an avatar.
  final BorderRadius borderRadius = AppRadii.sm,
  super.key,
}) extends StatefulWidget {
  /// Creates a skeleton.
  this;

  @override
  State<AppSkeleton> createState() => _AppSkeletonState();
}

/// Drives the sweep of the highlight.
class _AppSkeletonState()
    extends State<AppSkeleton>
    with SingleTickerProviderStateMixin {
  /// The opacity of the white highlight on a light surface. The dark theme
  /// needs a much fainter one, because its placeholder is nearly black.
  static const double _lightHighlightOpacity = 0.64;

  /// Runs from 0 to 1 once per sweep, and repeats while motion is allowed.
  late final AnimationController _sweep = AnimationController(
    vsync: this,
    duration: AppMotion.skeletonSweep,
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _sweep.stop();
    } else if (!_sweep.isAnimating) {
      _sweep.repeat();
    }
  }

  @override
  void dispose() {
    _sweep.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    final highlight = Theme.of(context).brightness == Brightness.dark
        ? AppPalette.whiteAlpha4
        : AppPalette.white.withValues(alpha: _lightHighlightOpacity);

    return ClipRRect(
      borderRadius: widget.borderRadius,
      child: ColoredBox(
        color: colors.muted,
        child: AnimatedBuilder(
          animation: _sweep,
          builder: (context, _) => DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: const Alignment(-1, -0.3),
                end: const Alignment(1, 0.3),
                stops: const [0.4, 0.5, 0.6],
                colors: [
                  highlight.withValues(alpha: 0),
                  highlight,
                  highlight.withValues(alpha: 0),
                ],
                transform: _SweepTransform(_sweep.value),
              ),
            ),
            child: SizedBox(width: widget.width, height: widget.height),
          ),
        ),
      ),
    );
  }
}

/// Moves the highlight from beyond the left edge to beyond the right edge as
/// the sweep progresses.
final class const _SweepTransform(
  /// How far the sweep is, from 0 to 1.
  final double progress,
) extends GradientTransform {
  @override
  Matrix4 transform(Rect bounds, {TextDirection? textDirection}) {
    return Matrix4.translationValues(bounds.width * (2 * progress - 1), 0, 0);
  }
}
