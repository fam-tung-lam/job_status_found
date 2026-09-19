import 'package:job_status_found/features/health/application/ports/health_repository.dart';
import 'package:job_status_found/features/health/domain/failures/health_check_failure.dart';
import 'package:job_status_found/features/health/infrastructure/clients/health_api_client.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// [HealthRepository] answered by the backend's `GET /health` endpoint.
///
/// Makes one request per check with no retry; the caller decides when to check
/// again. Throws [HealthCheckBackendUnreachableFailure] when the request cannot
/// complete, and [HealthCheckUnexpectedResponseFailure] for an error status
/// or an unknown body.
final class const ApiHealthRepository(
  /// Fetches the raw health response from the backend.
  final HealthApiClient _healthApiClient,
) implements HealthRepository {
  /// Creates the repository over the backend [HealthApiClient].
  this;

  @override
  Future<void> checkBackendHealth() async {
    try {
      await _healthApiClient.fetchHealthStatus();
    } on JobStatusFoundHttpClientException catch (exception, stackTrace) {
      Error.throwWithStackTrace(_toHealthCheckFailure(exception), stackTrace);
    } on FormatException catch (_, stackTrace) {
      Error.throwWithStackTrace(
        const HealthCheckUnexpectedResponseFailure(),
        stackTrace,
      );
    }
  }

  /// Classifies a failed request: a response the app cannot use becomes
  /// [HealthCheckUnexpectedResponseFailure], and any other failure
  /// [HealthCheckBackendUnreachableFailure].
  HealthCheckFailure _toHealthCheckFailure(
    JobStatusFoundHttpClientException exception,
  ) => switch (exception) {
    JobStatusFoundHttpClientBadResponse() ||
    JobStatusFoundHttpClientTransformTimeout() =>
      const HealthCheckUnexpectedResponseFailure(),
    JobStatusFoundHttpClientConnectionTimeout() ||
    JobStatusFoundHttpClientSendTimeout() ||
    JobStatusFoundHttpClientReceiveTimeout() ||
    JobStatusFoundHttpClientBadCertificate() ||
    JobStatusFoundHttpClientCancelled() ||
    JobStatusFoundHttpClientConnectionFailed() ||
    JobStatusFoundHttpClientUnknownFailure() =>
      const HealthCheckBackendUnreachableFailure(),
  };
}
