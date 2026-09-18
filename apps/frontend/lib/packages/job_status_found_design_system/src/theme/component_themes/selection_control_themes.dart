import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_opacity.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_radii.dart';

/// Returns [color], dimmed when [states] say the control is disabled.
Color _dimmedWhenDisabled(Color color, Set<WidgetState> states) =>
    states.contains(WidgetState.disabled)
    ? color.withValues(alpha: color.a * AppOpacity.disabled)
    : color;

/// Returns the look of every checkbox: a small rounded box that fills with
/// the primary color when checked.
CheckboxThemeData buildAppCheckboxTheme(AppColors colors) {
  return CheckboxThemeData(
    shape: const RoundedRectangleBorder(borderRadius: AppRadii.xs),
    side: BorderSide(color: colors.input),
    fillColor: WidgetStateProperty.resolveWith(
      (states) => _dimmedWhenDisabled(
        states.contains(WidgetState.selected)
            ? colors.primary
            : colors.background,
        states,
      ),
    ),
    checkColor: WidgetStatePropertyAll(colors.primaryForeground),
    overlayColor: const WidgetStatePropertyAll(Colors.transparent),
    splashRadius: 0,
  );
}

/// Returns the look of every radio button: a ring that gains a primary dot
/// when selected.
RadioThemeData buildAppRadioTheme(AppColors colors) {
  return RadioThemeData(
    fillColor: WidgetStateProperty.resolveWith(
      (states) => _dimmedWhenDisabled(
        states.contains(WidgetState.selected) ? colors.primary : colors.input,
        states,
      ),
    ),
    overlayColor: const WidgetStatePropertyAll(Colors.transparent),
    splashRadius: 0,
  );
}

/// Returns the look of every switch: a borderless track that turns primary
/// when on, with a thumb in the background color.
SwitchThemeData buildAppSwitchTheme(AppColors colors) {
  return SwitchThemeData(
    trackColor: WidgetStateProperty.resolveWith(
      (states) => _dimmedWhenDisabled(
        states.contains(WidgetState.selected) ? colors.primary : colors.input,
        states,
      ),
    ),
    thumbColor: WidgetStatePropertyAll(colors.background),
    trackOutlineColor: const WidgetStatePropertyAll(Colors.transparent),
    trackOutlineWidth: const WidgetStatePropertyAll(0),
    overlayColor: const WidgetStatePropertyAll(Colors.transparent),
    splashRadius: 0,
  );
}
