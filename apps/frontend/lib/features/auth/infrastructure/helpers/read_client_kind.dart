import 'package:flutter/foundation.dart';
import 'package:job_status_found/features/auth/domain/value_objects/client_kind.dart';

/// Reads the backend client-kind name for the current Flutter platform.
ClientKind readClientKind() {
  if (kIsWeb) return ClientKind.web;
  return defaultTargetPlatform == TargetPlatform.iOS
      ? ClientKind.ios
      : ClientKind.android;
}
