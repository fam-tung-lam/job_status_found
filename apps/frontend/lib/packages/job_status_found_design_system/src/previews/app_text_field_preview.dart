import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

/// Representative text field states for the widget previewer.
@Preview(name: 'App text field')
Widget buildAppTextFieldPreview() => MaterialApp(
  theme: AppTheme.light,
  home: const Scaffold(
    body: Padding(
      padding: EdgeInsets.all(AppSpacing.lg),
      child: AppTextField(
        label: 'Email Address',
        placeholder: 'Email Address',
        helperText: 'We will never share your email.',
      ),
    ),
  ),
);
