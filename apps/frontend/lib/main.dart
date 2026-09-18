import 'package:flutter/widgets.dart';
import 'package:get_it/get_it.dart';
import 'package:job_status_found/app/app.dart';
import 'package:job_status_found/app/app_router.dart';
import 'package:job_status_found/app/di.dart';
import 'package:job_status_found/settings.dart';

void main() {
  final getIt = GetIt.instance;
  configureDependencies(getIt, AppSettings.fromEnvironment());
  runApp(App(router: createAppRouter(getIt)));
}
