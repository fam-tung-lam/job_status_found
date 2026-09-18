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

## Backend connection

The app starts on a page that shows the backend's `GET /health` status. Start
the backend first (see `../backend/README.md`).

The backend URL comes from `--dart-define=API_BASE_URL=...` and defaults to
`http://localhost:8000`, which works for web and the iOS simulator.
The Android emulator reaches the host machine at `10.0.2.2`:

```shell
fvm flutter run -d emulator-5554 --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Debug Android builds allow plain `http`; release builds need an `https` URL.

## Checks

```shell
fvm flutter analyze
fvm dart format --output=none --set-exit-if-changed .
fvm flutter test
```
