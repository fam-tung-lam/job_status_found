import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_sizes.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_typography.dart';

/// A labeled text field with optional help, error, action, and obscure toggle.
class const AppTextField({
  /// Visible and semantic field label.
  required final String label,

  /// Placeholder shown while empty.
  required final String placeholder,

  /// Controls the current text.
  final TextEditingController? controller,

  /// Guidance shown below the field.
  final String? helperText,

  /// Live validation error shown below the field.
  final String? errorText,

  /// Action at the end of the label row.
  final Widget? labelAction,

  /// Whether the value starts hidden and can be revealed.
  final bool isObscured = false,

  /// Accessible reveal action copy when [isObscured] is true.
  final String? showObscuredTextTooltip,

  /// Accessible hide action copy when [isObscured] is true.
  final String? hideObscuredTextTooltip,

  /// Whether the field accepts input.
  final bool enabled = true,

  /// Autofill values describing the field.
  final Iterable<String>? autofillHints,

  /// Software keyboard suited to the value.
  final TextInputType? keyboardType,

  /// Action shown by the keyboard.
  final TextInputAction? textInputAction,

  /// Whether automatic correction is enabled.
  final bool autocorrect = true,

  /// Called after the text changes.
  final ValueChanged<String>? onChanged,

  /// Called after the keyboard action.
  final ValueChanged<String>? onSubmitted,

  /// Controls keyboard focus.
  final FocusNode? focusNode,

  /// Filters edits before they reach the controller.
  final List<TextInputFormatter>? inputFormatters,

  /// Maximum accepted character count.
  final int? maxLength,
  super.key,
}) extends StatefulWidget {
  /// Creates a design-system text field.
  this
    : assert(
        !isObscured ||
            (showObscuredTextTooltip != null &&
                hideObscuredTextTooltip != null),
        'Obscured fields require localized reveal and hide tooltips.',
      );

  @override
  State<AppTextField> createState() => _AppTextFieldState();
}

/// Tracks whether an obscured field is currently visible.
class _AppTextFieldState() extends State<AppTextField> {
  /// Whether the value is hidden.
  late bool _isHidden = widget.isObscured;

  @override
  Widget build(BuildContext context) {
    final colors = AppColors.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      spacing: AppSpacing.xs,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                widget.label,
                style: AppTypography.sm.copyWith(
                  fontWeight: AppTypography.medium,
                  color: colors.foreground,
                ),
              ),
            ),
            ?widget.labelAction,
          ],
        ),
        Semantics(
          textField: true,
          label: widget.label,
          liveRegion: widget.errorText != null,
          child: TextField(
            controller: widget.controller,
            focusNode: widget.focusNode,
            enabled: widget.enabled,
            obscureText: widget.isObscured && _isHidden,
            autofillHints: widget.autofillHints,
            keyboardType: widget.keyboardType,
            textInputAction: widget.textInputAction,
            autocorrect: widget.autocorrect,
            onChanged: widget.onChanged,
            onSubmitted: widget.onSubmitted,
            inputFormatters: widget.inputFormatters,
            maxLength: widget.maxLength,
            decoration: InputDecoration(
              hintText: widget.placeholder,
              helperText: widget.helperText,
              errorText: widget.errorText,
              constraints: const BoxConstraints(minHeight: AppSizes.controlXxl),
              counterText: '',
              suffixIconConstraints: const BoxConstraints(
                minWidth: AppSizes.controlXxl,
                minHeight: AppSizes.controlXxl,
              ),
              suffixIcon: widget.isObscured
                  ? IconButton(
                      tooltip: _isHidden
                          ? widget.showObscuredTextTooltip!
                          : widget.hideObscuredTextTooltip!,
                      onPressed: widget.enabled
                          ? () => setState(() => _isHidden = !_isHidden)
                          : null,
                      icon: Icon(
                        _isHidden
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                      ),
                    )
                  : null,
            ),
          ),
        ),
      ],
    );
  }
}
