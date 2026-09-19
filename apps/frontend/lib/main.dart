import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app.dart';
import 'package:job_status_found/app/app_router.dart';
import 'package:job_status_found/app/app_settings.dart';
import 'package:job_status_found/app/di.dart';
import 'package:job_status_found/features/auth/auth.dart';

void main() {
  usePathUrlStrategy();
  final getIt = GetIt.instance;
  configureDependencies(getIt, AppSettings.fromEnvironment());
  final authSessionCubit = getIt<AuthSessionCubit>();
  runApp(App(router: createAppRouter(getIt, authSessionCubit)));
  unawaited(authSessionCubit.restoreSession());
}
