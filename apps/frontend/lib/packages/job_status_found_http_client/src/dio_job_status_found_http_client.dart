import 'package:dio/dio.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client_exception.dart';

/// [JobStatusFoundHttpClient] backed by the `dio` package.
///
/// Makes one attempt per call with no retry. Every [DioException] is
/// translated into the matching [JobStatusFoundHttpClientException], keeping
/// its stack trace.
final class DioJobStatusFoundHttpClient({
  required Uri baseUrl,
  Duration connectTimeout = const Duration(seconds: 5),
  Duration sendTimeout = const Duration(seconds: 5),
  Duration receiveTimeout = const Duration(seconds: 10),
}) implements JobStatusFoundHttpClient {
  /// Creates a client that resolves every path against [baseUrl] and bounds
  /// each request by [connectTimeout], [sendTimeout], and [receiveTimeout].
  this;

  /// The Dio instance that sends every request, configured once from the
  /// constructor's base URL and timeouts.
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: baseUrl.toString(),
      connectTimeout: connectTimeout,
      sendTimeout: sendTimeout,
      receiveTimeout: receiveTimeout,
    ),
  );

  @override
  Future<Object?> get(
    String path, {
    Map<String, Object?> queryParameters = const {},
  }) async {
    try {
      final response = await _dio.get<Object?>(
        path,
        queryParameters: queryParameters,
      );
      return response.data;
    } on DioException catch (exception, stackTrace) {
      Error.throwWithStackTrace(
        _toJobStatusFoundHttpClientException(exception),
        stackTrace,
      );
    }
  }

  @override
  void close() => _dio.close();

  /// Converts [exception] into the [JobStatusFoundHttpClientException]
  /// subclass for its [DioExceptionType], carrying the request URL, and for a
  /// bad response its status code and body.
  JobStatusFoundHttpClientException _toJobStatusFoundHttpClientException(
    DioException exception,
  ) {
    final requestUri = exception.requestOptions.uri;
    return switch (exception.type) {
      DioExceptionType.connectionTimeout =>
        JobStatusFoundHttpClientConnectionTimeout(requestUri),
      DioExceptionType.sendTimeout => JobStatusFoundHttpClientSendTimeout(
        requestUri,
      ),
      DioExceptionType.receiveTimeout => JobStatusFoundHttpClientReceiveTimeout(
        requestUri,
      ),
      DioExceptionType.badCertificate => JobStatusFoundHttpClientBadCertificate(
        requestUri,
      ),
      DioExceptionType.badResponse => JobStatusFoundHttpClientBadResponse(
        requestUri,
        statusCode: exception.response?.statusCode,
        body: exception.response?.data,
      ),
      DioExceptionType.cancel => JobStatusFoundHttpClientCancelled(requestUri),
      DioExceptionType.connectionError =>
        JobStatusFoundHttpClientConnectionFailed(requestUri),
      DioExceptionType.transformTimeout =>
        JobStatusFoundHttpClientTransformTimeout(requestUri),
      DioExceptionType.unknown => JobStatusFoundHttpClientUnknownFailure(
        requestUri,
        cause: exception.error,
      ),
    };
  }
}
