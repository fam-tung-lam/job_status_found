import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Representative labeled divider for the widget previewer.
@Preview(name: 'App labeled divider')
Widget buildAppLabeledDividerPreview() => MaterialApp(
  theme: AppTheme.light,
  home: const Scaffold(
    body: Padding(
      padding: EdgeInsets.all(AppSpacing.lg),
      child: AppLabeledDivider(label: 'Or login with your email'),
    ),
  ),
);
