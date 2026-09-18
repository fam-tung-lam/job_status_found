# Networking

How Flutter calls one external API through an owned client.

## One client per API source

Give each external API its own [`Dio`](https://pub.dev/packages/dio) instance
and client class, with its own base URL, timeouts, and interceptors. APIs do not
share a client because their authentication and retry policies diverge.

A client exposes one method per endpoint, takes and returns DTOs, and holds no
business rules. Put cross-cutting headers, token refresh, retry, and request
logging in interceptors so endpoint methods do not repeat them.

Set connect, send, and receive timeouts explicitly. Accept a `CancelToken` on
any request whose caller can leave, and let that caller cancel through its own
lifecycle.

Bound retries in the interceptor that owns them: a capped attempt count,
exponential backoff with jitter, and only for requests the API says are safe to
repeat. A mobile client on a flaky connection retries far more often than the
developer who wrote the loop expects.

Nothing outside infrastructure imports Dio or sees a `Response`, status code, or
`DioException`.
[architecture.md](architecture.md#one-repository-port-per-concern) owns the
port-and-adapter boundary, and [models.md](models.md) owns domain failures.

Treat offline as an expected domain outcome, not an exception to log and
rethrow. Apply the record and sensitive-data rules in [logging.md](logging.md)
to every interceptor.
