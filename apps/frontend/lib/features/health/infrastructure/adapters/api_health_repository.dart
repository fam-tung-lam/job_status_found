import 'package:job_status_found/features/health/application/dtos/health_status_response_dto.dart';
import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// [HealthRepository] answered by the backend's `GET /health` endpoint.
///
/// Makes one request per check with no retry; the caller decides when to check
/// again. Throws [HealthCheckBackendUnreachable] when the request cannot
/// complete, and [HealthCheckUnexpectedResponse] for an error status or an
/// unknown body.
final class const ApiHealthRepository(
  /// Fetches the raw health response from the backend.
  final HealthApiClient _client,
) implements HealthRepository {
  /// Creates the repository over the backend [HealthApiClient].
  this;

  @override
  Future<void> check() async {
    try {
      _ensureHealthy(await _client.getHealth());
    } on JobStatusFoundHttpClientException catch (exception, stackTrace) {
      Error.throwWithStackTrace(_toFailure(exception), stackTrace);
    } on FormatException catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const HealthCheckUnexpectedResponse(),
        stackTrace,
      );
    }
  }

  /// Returns normally when the wire status word is `ok`.
  ///
  /// Throws [FormatException] for a word this app does not know.
  void _ensureHealthy(HealthStatusResponseDto response) {
    if (response.status != 'ok') {
      throw FormatException('Unknown health status in $response.');
    }
  }

  /// Classifies a failed request: a response the app cannot use becomes
  /// [HealthCheckUnexpectedResponse], and any other failure
  /// [HealthCheckBackendUnreachable].
  HealthCheckFailure _toFailure(JobStatusFoundHttpClientException exception) =>
      switch (exception) {
        JobStatusFoundHttpClientBadResponse() ||
        JobStatusFoundHttpClientTransformTimeout() =>
          const HealthCheckUnexpectedResponse(),
        JobStatusFoundHttpClientConnectionTimeout() ||
        JobStatusFoundHttpClientSendTimeout() ||
        JobStatusFoundHttpClientReceiveTimeout() ||
        JobStatusFoundHttpClientBadCertificate() ||
        JobStatusFoundHttpClientCancelled() ||
        JobStatusFoundHttpClientConnectionFailed() ||
        JobStatusFoundHttpClientUnknownFailure() =>
          const HealthCheckBackendUnreachable(),
      };
}
