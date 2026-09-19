import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Prompt and link that switch between sign-in and sign-up.
class const AuthSwitchPrompt({
  required final String prompt,
  required final String actionLabel,
  required final VoidCallback? onPressed,
  super.key,
}) extends StatelessWidget {
  /// Creates a switch prompt.
  this;

  @override
  Widget build(BuildContext context) => Wrap(
    alignment: WrapAlignment.center,
    crossAxisAlignment: WrapCrossAlignment.center,
    children: [
      Text(prompt),
      const SizedBox(width: AppSpacing.xs),
      ConstrainedBox(
        constraints: const BoxConstraints(minHeight: AppSizes.controlXxl),
        child: TextButton(onPressed: onPressed, child: Text(actionLabel)),
      ),
    ],
  );
}
