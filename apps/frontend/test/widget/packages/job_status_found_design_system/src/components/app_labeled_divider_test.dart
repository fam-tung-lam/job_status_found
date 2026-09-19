import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

void main() {
  testWidgets('keeps the label between two flexible dividers', (tester) async {
    // Given: the labeled divider in a bounded row.
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light,
        home: const Scaffold(
          body: AppLabeledDivider(label: 'Or continue with email'),
        ),
      ),
    );

    // When: the component renders.
    final dividers = find.byType(Divider);

    // Then: its label separates two rules without hard-coded widths.
    expect(find.text('Or continue with email'), findsOneWidget);
    expect(dividers, findsNWidgets(2));
    expect(
      find.ancestor(of: dividers, matching: find.byType(Expanded)),
      findsNWidgets(2),
    );
  });
}
