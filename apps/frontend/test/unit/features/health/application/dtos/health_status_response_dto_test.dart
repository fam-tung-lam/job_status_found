import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/application/dtos/health_status_response_dto.dart';

void main() {
  group('HealthStatusResponseDTO', () {
    test('rejects a body without a string status', () {
      // Given: a body whose status is missing.
      const json = <String, Object?>{'state': 'ok'};

      // When: the body is decoded.
      HealthStatusResponseDTO decode() =>
          HealthStatusResponseDTO.fromJson(json);

      // Then: decoding fails as a format error.
      expect(decode, throwsFormatException);
    });
  });
}
