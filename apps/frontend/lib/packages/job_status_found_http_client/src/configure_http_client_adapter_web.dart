import 'package:dio/browser.dart';
import 'package:dio/dio.dart';

/// Enables browser credentials so the refresh cookie travels cross-origin.
void configureHttpClientAdapter(Dio dio) {
  dio.httpClientAdapter = BrowserHttpClientAdapter()..withCredentials = true;
}
