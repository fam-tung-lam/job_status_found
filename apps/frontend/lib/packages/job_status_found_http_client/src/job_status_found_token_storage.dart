import 'package:job_status_found/packages/job_status_found_http_client/src/job_status_found_http_client.dart';

/// Persistence used by the HTTP client for session tokens.
abstract interface class JobStatusFoundTokenStorage() {
  /// Creates token storage.
  this;

  /// Reads the stored tokens, or `null` when none exist.
  Future<JobStatusFoundAuthTokens?> read();

  /// Replaces the stored tokens.
  Future<void> write(JobStatusFoundAuthTokens tokens);

  /// Deletes all stored tokens.
  Future<void> delete();
}
