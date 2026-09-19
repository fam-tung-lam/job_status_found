import 'package:job_status_found/features/health/application/dtos/health_status_response_dto.dart';
import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Calls the backend's health endpoint.
final class const HealthApiClient(
  /// Sends the request to the backend and decodes its JSON body.
  final JobStatusFoundHttpClient _httpClient,
) {
  /// Creates the client over the backend [JobStatusFoundHttpClient].
  this;

  /// Fetches `GET /health`.
  ///
  /// Throws [JobStatusFoundHttpClientException] when the request fails, and
  /// [FormatException] when the body is not the documented JSON object.
  Future<HealthStatusResponseDTO> fetchHealthStatus() async {
    final body = await _httpClient.get('/health');

    if (body is! Map<String, Object?>) {
      throw FormatException('Expected a JSON object from /health, got $body.');
    }
    return HealthStatusResponseDTO.fromJson(body);
  }
}
