import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/components/app_spinner.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/app_colors.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/theme/component_themes/app_button_style.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_motion.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_spacing.dart';

/// A button with a text label, in one of the [AppButtonVariant] looks.
///
/// The button shrinks slightly while pressed, unless the platform asks for
/// reduced motion. Requires an ancestor theme built by `AppTheme`.
class const AppButton({
  /// The text on the button.
  required final String label,

  /// Called when the user activates the button; `null` disables the button.
  required final VoidCallback? onPressed,

  /// How much the button stands out, and what its action means.
  final AppButtonVariant variant = AppButtonVariant.primary,

  /// How tall the button is.
  final AppButtonSize size = AppButtonSize.md,

  /// The icon before the label, if any.
  final IconData? leadingIcon,

  /// The icon after the label, if any.
  final IconData? trailingIcon,

  /// Whether the action is in progress. While `true`, a spinner replaces the
  /// content without changing the button's width, and the button ignores
  /// activation.
  final bool isLoading = false,
  super.key,
}) extends StatefulWidget {
  /// Creates a button.
  this;

  @override
  State<AppButton> createState() => _AppButtonState();
}

/// Tracks whether the button is pressed, which drives the press animation.
class _AppButtonState() extends State<AppButton> {
  /// Reports the pressed state of the Material button below.
  final WidgetStatesController _statesController = WidgetStatesController();

  /// Whether the user is holding the button down.
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _statesController.addListener(_handleStatesChanged);
  }

  @override
  void dispose() {
    _statesController.dispose();
    super.dispose();
  }

  /// Rebuilds when the pressed state changes, and ignores every other state.
  void _handleStatesChanged() {
    final isPressed = _statesController.value.contains(WidgetState.pressed);
    if (isPressed != _isPressed) {
      setState(() => _isPressed = isPressed);
    }
  }

  @override
  Widget build(BuildContext context) {
    final style = buildAppButtonStyle(
      colors: AppColors.of(context),
      brightness: Theme.of(context).brightness,
      variant: widget.variant,
      size: widget.size,
    );
    final onPressed = widget.isLoading ? null : widget.onPressed;
    final content = _ButtonContent(
      label: widget.label,
      size: widget.size,
      leadingIcon: widget.leadingIcon,
      trailingIcon: widget.trailingIcon,
      isLoading: widget.isLoading,
    );
    final button = switch (widget.variant) {
      AppButtonVariant.primary ||
      AppButtonVariant.secondary ||
      AppButtonVariant.destructive => FilledButton(
        onPressed: onPressed,
        style: style,
        statesController: _statesController,
        child: content,
      ),
      AppButtonVariant.outline ||
      AppButtonVariant.destructiveOutline => OutlinedButton(
        onPressed: onPressed,
        style: style,
        statesController: _statesController,
        child: content,
      ),
      AppButtonVariant.ghost || AppButtonVariant.link => TextButton(
        onPressed: onPressed,
        style: style,
        statesController: _statesController,
        child: content,
      ),
    };

    final isScaledDown = _isPressed && !MediaQuery.disableAnimationsOf(context);
    return AnimatedScale(
      scale: isScaledDown ? AppMotion.pressedScale : 1,
      duration: AppMotion.fast,
      curve: AppMotion.easeOut,
      child: button,
    );
  }
}

/// The icons and label of a button, or a spinner over their hidden copy while
/// the action is in progress.
class const _ButtonContent({
  /// The text on the button.
  required final String label,

  /// The button size, which sets the gap between an icon and the label.
  required final AppButtonSize size,

  /// The icon before the label, if any.
  required final IconData? leadingIcon,

  /// The icon after the label, if any.
  required final IconData? trailingIcon,

  /// Whether the spinner replaces the content.
  required final bool isLoading,
}) extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final content = Row(
      mainAxisSize: MainAxisSize.min,
      spacing: switch (size) {
        AppButtonSize.xs => AppSpacing.xs,
        AppButtonSize.sm => AppSpacing.xs + AppSpacing.xxs,
        AppButtonSize.md ||
        AppButtonSize.lg ||
        AppButtonSize.xl ||
        AppButtonSize.xxl => AppSpacing.sm,
      },
      children: [
        if (leadingIcon != null) Icon(leadingIcon),
        Flexible(child: Text(label, overflow: TextOverflow.ellipsis)),
        if (trailingIcon != null) Icon(trailingIcon),
      ],
    );
    if (!isLoading) {
      return content;
    }
    return Stack(
      alignment: Alignment.center,
      children: [
        // The hidden content keeps the button at its resting width.
        Visibility.maintain(visible: false, child: content),
        const AppSpinner(),
      ],
    );
  }
}
