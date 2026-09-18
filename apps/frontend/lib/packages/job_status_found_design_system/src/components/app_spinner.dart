import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';

/// A thin ring that spins while something of unknown duration is in progress.
///
/// The ring takes the color of the surrounding text by default, so it matches
/// the label of a button or the text of a sentence it sits in.
class const AppSpinner({
  /// The diameter of the ring, in logical pixels.
  final double size = AppSizes.iconMd,

  /// The color of the ring; the surrounding text color when `null`.
  final Color? color,

  /// What a screen reader announces for the ring; nothing when `null`, which
  /// suits a spinner beside visible text that already says what is loading.
  final String? semanticLabel,
  super.key,
}) extends StatelessWidget {
  /// Creates a spinner.
  this;

  @override
  Widget build(BuildContext context) {
    return SizedBox.square(
      dimension: size,
      child: CircularProgressIndicator(
        color: color ?? DefaultTextStyle.of(context).style.color,
        strokeWidth: AppSizes.focusRing,
        strokeCap: StrokeCap.round,
        semanticsLabel: semanticLabel,
      ),
    );
  }
}
