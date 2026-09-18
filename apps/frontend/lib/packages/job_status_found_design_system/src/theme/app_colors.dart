import 'package:flutter/material.dart';
import 'package:job_status_found/packages/job_status_found_design_system/src/tokens/app_palette.dart';

/// The semantic colors of the current theme, named by role.
///
/// A surface color pairs with a `Foreground` color that stays readable on it.
/// A status color, such as [success], paints icons and tinted fills, and its
/// `Foreground` paints text of the same status. Read the colors with
/// [AppColors.of]; `AppTheme` installs [light] and [dark].
@immutable
final class const AppColors({
  /// The page behind everything.
  required final Color background,

  /// Text and icons on [background].
  required final Color foreground,

  /// The surface of a card.
  required final Color card,

  /// Text and icons on [card].
  required final Color cardForeground,

  /// The surface of a menu, dialog, or tooltip that floats above the page.
  required final Color popover,

  /// Text and icons on [popover].
  required final Color popoverForeground,

  /// The fill of the main action.
  required final Color primary,

  /// Text and icons on [primary].
  required final Color primaryForeground,

  /// The translucent fill of a secondary action.
  required final Color secondary,

  /// Text and icons on [secondary].
  required final Color secondaryForeground,

  /// The translucent fill of a quiet area, such as a skeleton.
  required final Color muted,

  /// Secondary text, such as a description or a placeholder.
  required final Color mutedForeground,

  /// The translucent fill of a hovered or selected item.
  required final Color accent,

  /// Text and icons on [accent].
  required final Color accentForeground,

  /// The translucent hairline between and around surfaces.
  required final Color border,

  /// The translucent border of a control, such as a text field.
  required final Color input,

  /// The ring around a widget that has keyboard focus.
  required final Color ring,

  /// The fill of a destructive action, and the icon of an error.
  required final Color destructive,

  /// Error text.
  required final Color destructiveForeground,

  /// The icon and tint of a success.
  required final Color success,

  /// Success text.
  required final Color successForeground,

  /// The icon and tint of a warning.
  required final Color warning,

  /// Warning text.
  required final Color warningForeground,

  /// The icon and tint of neutral information.
  required final Color info,

  /// Information text.
  required final Color infoForeground,

  /// The surface of the navigation sidebar.
  required final Color sidebar,

  /// Text and icons on [sidebar].
  required final Color sidebarForeground,

  /// The translucent hairline beside and inside [sidebar].
  required final Color sidebarBorder,
}) extends ThemeExtension<AppColors> {
  /// Creates a set of semantic colors.
  this;

  /// The colors of the light theme.
  static const light = AppColors(
    background: AppPalette.white,
    foreground: AppPalette.neutral800,
    card: AppPalette.white,
    cardForeground: AppPalette.neutral800,
    popover: AppPalette.white,
    popoverForeground: AppPalette.neutral800,
    primary: AppPalette.neutral800,
    primaryForeground: AppPalette.neutral50,
    secondary: AppPalette.blackAlpha4,
    secondaryForeground: AppPalette.neutral800,
    muted: AppPalette.blackAlpha4,
    mutedForeground: AppPalette.neutral500Darkened,
    accent: AppPalette.blackAlpha4,
    accentForeground: AppPalette.neutral800,
    border: AppPalette.blackAlpha8,
    input: AppPalette.blackAlpha10,
    ring: AppPalette.neutral400,
    destructive: AppPalette.red500,
    destructiveForeground: AppPalette.red700,
    success: AppPalette.emerald500,
    successForeground: AppPalette.emerald700,
    warning: AppPalette.amber500,
    warningForeground: AppPalette.amber700,
    info: AppPalette.blue500,
    infoForeground: AppPalette.blue700,
    sidebar: AppPalette.neutral50,
    sidebarForeground: AppPalette.neutral800Softened,
    sidebarBorder: AppPalette.blackAlpha6,
  );

  /// The colors of the dark theme.
  static const dark = AppColors(
    background: AppPalette.neutral950Lifted4,
    foreground: AppPalette.neutral100,
    card: AppPalette.neutral950Lifted6,
    cardForeground: AppPalette.neutral100,
    popover: AppPalette.neutral950Lifted6,
    popoverForeground: AppPalette.neutral100,
    primary: AppPalette.neutral100,
    primaryForeground: AppPalette.neutral800,
    secondary: AppPalette.whiteAlpha4,
    secondaryForeground: AppPalette.neutral100,
    muted: AppPalette.whiteAlpha4,
    mutedForeground: AppPalette.neutral500Lightened,
    accent: AppPalette.whiteAlpha4,
    accentForeground: AppPalette.neutral100,
    border: AppPalette.whiteAlpha6,
    input: AppPalette.whiteAlpha8,
    ring: AppPalette.neutral500,
    destructive: AppPalette.red500Lightened,
    destructiveForeground: AppPalette.red400,
    success: AppPalette.emerald500,
    successForeground: AppPalette.emerald400,
    warning: AppPalette.amber500,
    warningForeground: AppPalette.amber400,
    info: AppPalette.blue500,
    infoForeground: AppPalette.blue400,
    sidebar: AppPalette.neutral950Lifted3,
    sidebarForeground: AppPalette.neutral100Softened,
    sidebarBorder: AppPalette.whiteAlpha5,
  );

  /// Returns the colors of the theme that encloses [context].
  ///
  /// Requires an ancestor `Theme` built by `AppTheme`, which `MaterialApp`
  /// provides when it is given `AppTheme.light` or `AppTheme.dark`.
  static AppColors of(BuildContext context) {
    final colors = Theme.of(context).extension<AppColors>();
    assert(
      colors != null,
      'No AppColors found. Give MaterialApp a theme built by AppTheme.',
    );
    return colors!;
  }

  // The framework requires this override but never calls it, and no caller
  // needs to change single colors, so it takes no parameters.
  @override
  AppColors copyWith() => this;

  /// Returns the colors that are [t] of the way from these colors to [other],
  /// which the framework shows while it animates between two themes.
  @override
  AppColors lerp(AppColors? other, double t) {
    if (other == null) {
      return this;
    }
    Color mix(Color from, Color to) => Color.lerp(from, to, t)!;
    return AppColors(
      background: mix(background, other.background),
      foreground: mix(foreground, other.foreground),
      card: mix(card, other.card),
      cardForeground: mix(cardForeground, other.cardForeground),
      popover: mix(popover, other.popover),
      popoverForeground: mix(popoverForeground, other.popoverForeground),
      primary: mix(primary, other.primary),
      primaryForeground: mix(primaryForeground, other.primaryForeground),
      secondary: mix(secondary, other.secondary),
      secondaryForeground: mix(secondaryForeground, other.secondaryForeground),
      muted: mix(muted, other.muted),
      mutedForeground: mix(mutedForeground, other.mutedForeground),
      accent: mix(accent, other.accent),
      accentForeground: mix(accentForeground, other.accentForeground),
      border: mix(border, other.border),
      input: mix(input, other.input),
      ring: mix(ring, other.ring),
      destructive: mix(destructive, other.destructive),
      destructiveForeground: mix(
        destructiveForeground,
        other.destructiveForeground,
      ),
      success: mix(success, other.success),
      successForeground: mix(successForeground, other.successForeground),
      warning: mix(warning, other.warning),
      warningForeground: mix(warningForeground, other.warningForeground),
      info: mix(info, other.info),
      infoForeground: mix(infoForeground, other.infoForeground),
      sidebar: mix(sidebar, other.sidebar),
      sidebarForeground: mix(sidebarForeground, other.sidebarForeground),
      sidebarBorder: mix(sidebarBorder, other.sidebarBorder),
    );
  }
}
