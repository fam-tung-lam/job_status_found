import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client_exception.dart';

/// HTTP access to the job_status_found API, independent of the HTTP package
/// that implements it.
abstract interface class JobStatusFoundHttpClient() {
  /// Creates the client.
  this;

  /// Sends `GET` to [path], resolved against the API base URL, and returns the
  /// decoded JSON body.
  ///
  /// The body is a `Map<String, Object?>`, `List<Object?>`, `String`, `num`,
  /// `bool`, or `null`, as the server sent it. Throws a
  /// [JobStatusFoundHttpClientException] when the request does not produce a
  /// 2xx response.
  Future<Object?> get(
    String path, {
    Map<String, Object?> queryParameters = const {},
  });

  /// Releases the connections this client holds.
  ///
  /// Call once, when the client is no longer used.
  void close();
}
