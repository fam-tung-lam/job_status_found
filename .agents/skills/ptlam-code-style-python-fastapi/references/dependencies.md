# FastAPI Dependencies

How request-scoped capabilities, cleanup, authentication, and authorization
enter the HTTP boundary.

Declare a dependency as a typed callable. Prefer
`Annotated[T, Depends(provider)]`, and store that annotation in a named alias
when several handlers use the same capability. Pass the callable to `Depends`
without calling it.

Dependencies own framework concerns: an authenticated principal, a request
database session, settings, correlation context, and an external client borrowed
for the request. A feature provider assembles its repository and use case from
those. Use cases and domain code receive ordinary typed arguments and never
import `Depends`.

Put feature providers in `features/<feature>/di.py`. That file is the only
feature surface that imports both FastAPI dependency mechanics and concrete
infrastructure adapters. Presentation imports the provider and the use-case
type; application code depends on the port; infrastructure implements it.

## Own cleanup with `yield`

A dependency that acquires a resource yields once. Put cleanup in `finally` or
inside its context manager. Roll back an unfinished transaction after a failure
and close the session on every exit. The use case still decides whether its
operation commits; dependency cleanup does not choose business policy.

Pick sync or async dependency syntax from the resource's API. Match any
dependency-scope option to the installed FastAPI version and the response
lifetime; a streaming response can outlive the handler's return.

The [dependency](https://fastapi.tiangolo.com/tutorial/dependencies/) and
[yield dependency](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
links identify the features; they are not required reading. When caching, scope,
or teardown behaves differently, read the locked packages and prove the resource
lifetime with a focused local test.

## Fail closed

Authenticate in one dependency and return a typed principal or credential
context. Authorize as close as possible to the protected operation. Distinguish
missing or invalid authentication from an authenticated caller without
permission, following the API's stable 401 and 403 contract.

Attach the scheme's required `WWW-Authenticate` header to a 401. When OAuth
scopes are part of the public contract, declare them with `Security` and enforce
them in the owning dependency.

Use a decorator dependency for a guard whose value no handler needs, or prefix
an injected guard parameter with `_` when the project prefers visible
signatures. Never read credentials again inside the service.

Finish when each request-scoped capability has one provider, one cleanup path,
and an exact callable a test can override.
