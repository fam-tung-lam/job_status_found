# job_status_found_design_system

The look of the app: design tokens, the Material themes built from them, and
the components that features compose. The look follows the Kaneo web app:
neutral ink on white (or near-black), hairline translucent borders, compact
controls, the Geist typeface, and status colors used as light tints.

Import only `job_status_found_design_system.dart`, never a file under `src/`.

## Layout

```text
job_status_found_design_system/
├── job_status_found_design_system.dart  # the public surface
└── src/
    ├── tokens/                # raw values; depend on nothing
    │   ├── app_palette.dart     # raw colors; private to this folder
    │   ├── app_spacing.dart     # padding, margins, gaps
    │   ├── app_radii.dart       # corner radii
    │   ├── app_sizes.dart       # control heights, icon sizes, hairline
    │   ├── app_typography.dart  # typeface, weights, type scale
    │   ├── app_shadows.dart     # xs, sm, lg
    │   ├── app_opacity.dart     # disabled, hover, tints
    │   └── app_motion.dart      # durations and curves
    ├── theme/                 # tokens turned into Flutter theme objects
    │   ├── app_colors.dart        # semantic colors, a ThemeExtension
    │   ├── app_theme.dart         # AppTheme.light and AppTheme.dark
    │   ├── app_color_scheme.dart  # semantic colors to Material roles
    │   ├── app_text_theme.dart    # type scale to Material text roles
    │   └── component_themes/      # one look per stock Material widget family
    ├── components/            # one public widget per file
    │   ├── app_button.dart  app_badge.dart  app_card.dart  app_alert.dart
    │   └── app_empty_state.dart  app_skeleton.dart  app_spinner.dart
    └── previews/              # catalog for the Flutter widget previewer
```

Dependencies point one way: `components` to `theme` to `tokens`.

## Use it

- `MaterialApp(theme: AppTheme.light, darkTheme: AppTheme.dark)` installs the
  look. Every component requires one of these themes above it.
- Colors: `AppColors.of(context).mutedForeground`. Never a `Color(0x…)`
  literal or a `Colors.*` constant in a feature.
- Everything else: `AppSpacing.lg`, `AppRadii.lg`, `AppTypography.sm`,
  `AppShadows.xs`, `AppMotion.fast`, `AppSizes.iconMd`.
- Stock Material widgets, such as `TextField`, `Checkbox`, `Switch`, and
  `showDialog`, already follow the theme.

## See it

```shell
fvm flutter widget-preview start
```

The previewer shows every component in both themes. It does not load the
app's fonts, so text there falls back to the platform typeface.

## Change it

| To add                        | Do this                                                                        |
|-------------------------------|--------------------------------------------------------------------------------|
| A raw value                   | Add it to the matching file in `src/tokens/`                                   |
| A color role                  | Add the field, both theme values, and the `lerp` line in `app_colors.dart`     |
| A look for a Material widget  | Add a builder in `src/theme/component_themes/` and wire it in `app_theme.dart` |
| A component two features need | Add `src/components/app_<name>.dart`, export it, add a preview and a test      |

The Geist font files live in `apps/frontend/assets/fonts/geist/` and are
declared under `flutter: fonts:` in `apps/frontend/pubspec.yaml`, as Flutter
recommends for an app. Geist is licensed under the SIL Open Font License;
`OFL.txt` must stay beside the font files. When this folder becomes its own
package, move the files into it and give the family a `package:` name.
