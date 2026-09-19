import 'package:equatable/equatable.dart';

/// The JSON body the backend returns from `GET /health`.
final class const HealthStatusResponseDTO({
  /// The backend status.
  required final HealthStatusResponseValue status,
}) extends Equatable {
  /// Creates the DTO from its wire fields.
  this;

  /// Decodes the wire body, such as `{"status": "ok"}`.
  ///
  /// Throws [FormatException] when `status` is missing or unknown.
  factory fromJson(Map<String, Object?> json) {
    final status = json['status'];
    if (status != HealthStatusResponseValue.ok.wireName) {
      throw FormatException('Expected status "ok" in $json.');
    }
    return const HealthStatusResponseDTO(status: HealthStatusResponseValue.ok);
  }

  @override
  List<Object?> get props => [status];
}

/// Health status values supported by this app version.
enum HealthStatusResponseValue(
  /// The response value returned by the backend.
  final String wireName,
) {
  /// The backend can serve requests.
  ok('ok'),
}
