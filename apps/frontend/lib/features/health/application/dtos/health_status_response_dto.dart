import 'package:equatable/equatable.dart';

/// The JSON body the backend returns from `GET /health`.
final class const HealthStatusResponseDto({
  /// The raw status word, which is `"ok"` in the current contract.
  required final String status,
}) extends Equatable {
  /// Creates the DTO from its wire fields.
  this;

  /// Decodes the wire body, such as `{"status": "ok"}`.
  ///
  /// Throws [FormatException] when `status` is missing or not a string.
  factory fromJson(Map<String, Object?> json) {
    final status = json['status'];
    if (status is! String) {
      throw FormatException('Expected a string "status" in $json.');
    }
    return HealthStatusResponseDto(status: status);
  }

  /// Encodes the DTO as its wire body.
  Map<String, Object?> toJson() => {'status': status};

  @override
  List<Object?> get props => [status];
}
