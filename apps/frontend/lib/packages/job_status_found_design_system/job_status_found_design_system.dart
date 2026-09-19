/// The look of the job_status_found app: design tokens, the Material themes
/// built from them, and the components that features compose.
///
/// Give `MaterialApp` the themes of `AppTheme`. Build feature UI from the
/// components, and take every remaining color from `AppColors.of` and every
/// distance, radius, text style, shadow, and duration from the tokens.
///
/// The raw color palette stays private, so a widget cannot fix a color that
/// ignores the dark theme. Nothing in this folder imports the rest of the app,
/// so the folder can move into its own Dart package.
library;

export 'src/components/app_alert.dart';
export 'src/components/app_badge.dart';
export 'src/components/app_button.dart';
export 'src/components/app_card.dart';
export 'src/components/app_empty_state.dart';
export 'src/components/app_labeled_divider.dart';
export 'src/components/app_skeleton.dart';
export 'src/components/app_spinner.dart';
export 'src/components/app_text_field.dart';
export 'src/theme/app_colors.dart';
export 'src/theme/app_theme.dart';
export 'src/theme/component_themes/app_button_style.dart'
    show AppButtonSize, AppButtonVariant;
export 'src/tokens/app_motion.dart';
export 'src/tokens/app_opacity.dart';
export 'src/tokens/app_radii.dart';
export 'src/tokens/app_shadows.dart';
export 'src/tokens/app_sizes.dart';
export 'src/tokens/app_spacing.dart';
export 'src/tokens/app_typography.dart';
