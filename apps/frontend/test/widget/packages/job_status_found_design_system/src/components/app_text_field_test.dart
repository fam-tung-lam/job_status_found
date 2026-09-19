import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/packages/job_status_found_design_system/job_status_found_design_system.dart';

void main() {
  testWidgets('shows one live validation message and can reveal a password', (
    tester,
  ) async {
    // Given: an obscured field with a validation failure.
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light,
        home: const Scaffold(
          body: AppTextField(
            label: 'Password',
            placeholder: 'Password',
            isObscured: true,
            showObscuredTextTooltip: 'Show password',
            hideObscuredTextTooltip: 'Hide password',
            errorText: 'Enter your password.',
          ),
        ),
      ),
    );

    // When: the component renders and the reveal action is activated.
    expect(find.text('Enter your password.'), findsOneWidget);
    expect(
      tester.widget<TextField>(find.byType(TextField)).obscureText,
      isTrue,
    );
    await tester.tap(find.byTooltip('Show password'));
    await tester.pump();

    // Then: the same field reveals its value without losing its error.
    expect(
      tester.widget<TextField>(find.byType(TextField)).obscureText,
      isFalse,
    );
    expect(find.text('Enter your password.'), findsOneWidget);
  });
}
