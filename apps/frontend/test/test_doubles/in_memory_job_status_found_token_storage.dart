import 'package:job_status_found/packages/job_status_found_http_client/job_status_found_http_client.dart';

/// Volatile token storage for tests that exercise the HTTP client.
final class InMemoryJobStatusFoundTokenStorage()
    implements JobStatusFoundTokenStorage {
  /// Creates empty in-memory storage.
  this;

  /// Tokens currently held by the test double.
  JobStatusFoundAuthTokens? _tokens;

  @override
  Future<void> delete() async => _tokens = null;

  @override
  Future<JobStatusFoundAuthTokens?> read() async => _tokens;

  @override
  Future<void> write(JobStatusFoundAuthTokens tokens) async => _tokens = tokens;
}
