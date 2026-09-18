import 'package:flutter_test/flutter_test.dart';
import 'package:job_status_found/features/health/application/dtos/health_status_response_dto.dart';

void main() {
  group('HealthStatusResponseDto', () {
    test('decodes the documented backend body', () {
      // Given: the example body the backend publishes for GET /health.
      const json = <String, Object?>{'status': 'ok'};

      // When: the body is decoded.
      final dto = HealthStatusResponseDto.fromJson(json);

      // Then: the DTO carries the status word.
      expect(dto, const HealthStatusResponseDto(status: 'ok'));
    });

    test('survives a round trip through JSON', () {
      // Given: a decoded health response.
      const dto = HealthStatusResponseDto(status: 'ok');

      // When: it is encoded and decoded again.
      final roundTripped = HealthStatusResponseDto.fromJson(dto.toJson());

      // Then: the result equals the original.
      expect(roundTripped, dto);
    });

    test('rejects a body without a string status', () {
      // Given: a body whose status is missing.
      const json = <String, Object?>{'state': 'ok'};

      // When: the body is decoded.
      HealthStatusResponseDto decode() =>
          HealthStatusResponseDto.fromJson(json);

      // Then: decoding fails as a format error.
      expect(decode, throwsFormatException);
    });
  });
}
