/// A request to the job_status_found API that did not produce a response
/// body.
///
/// One variant per way a request can fail, independent of the HTTP package
/// underneath.
sealed class JobStatusFoundHttpClientException(
  /// The full URL of the failed request.
  final Uri requestUri,
) implements Exception {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The connection could not be opened before the connect timeout.
final class JobStatusFoundHttpClientConnectionTimeout(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The request body could not be sent before the send timeout.
final class JobStatusFoundHttpClientSendTimeout(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The response did not arrive before the receive timeout.
final class JobStatusFoundHttpClientReceiveTimeout(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The server's TLS certificate was rejected.
final class JobStatusFoundHttpClientBadCertificate(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The server answered with a status code outside 2xx.
final class JobStatusFoundHttpClientBadResponse(
  super.requestUri, {

  /// The HTTP status code, or `null` when the transport reported none.
  required final int? statusCode,

  /// The decoded response body, or `null` when the response had none.
  required final Object? body,
}) extends JobStatusFoundHttpClientException {
  /// Creates the exception for the [statusCode] and [body] returned by
  /// [requestUri].
  this;
}

/// The caller cancelled the request.
final class JobStatusFoundHttpClientCancelled(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The connection failed, for example because nothing listens at the host or
/// the browser blocked the request.
final class JobStatusFoundHttpClientConnectionFailed(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The response could not be decoded before the transform timeout.
final class JobStatusFoundHttpClientTransformTimeout(super.requestUri)
    extends JobStatusFoundHttpClientException {
  /// Creates the exception for the request to [requestUri].
  this;
}

/// The request failed for a reason the HTTP package did not classify.
final class JobStatusFoundHttpClientUnknownFailure(
  super.requestUri, {

  /// The underlying failure, or `null` when the HTTP package gave none.
  required final Object? cause,
}) extends JobStatusFoundHttpClientException {
  /// Creates the exception for the unclassified [cause] of the request to
  /// [requestUri].
  this;
}
