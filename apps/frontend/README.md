# job_status_found frontend

Flutter app for web, iOS, and Android. The Flutter SDK is pinned by FVM in
`.fvmrc` (Flutter 3.47.2).

```shell
# install the pinned SDK and dependencies
fvm install
fvm flutter pub get

# run on a device or in the browser
fvm flutter run
fvm flutter run -d chrome
```

## Checks

```shell
fvm flutter analyze
fvm dart format --output=none --set-exit-if-changed .
fvm flutter test
```
