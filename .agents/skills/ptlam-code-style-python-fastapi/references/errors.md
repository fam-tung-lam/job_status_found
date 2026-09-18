# Python and FastAPI Errors

How Python code reports a failure without losing its cause or leaking an
implementation boundary, and how an application failure becomes one stable HTTP
response without coupling the layers below to the framework.

## Raise and translate in Python

Raise a built-in exception when its meaning is exact: `TypeError` for an
unsupported kind, `ValueError` for an invalid value, `RuntimeError` for an
invalid operation state. Use a domain exception when callers need to tell one
stable failure from another.

Catch the narrowest exception the current boundary can handle, then recover,
translate it once, or re-raise it. Use `raise NewError(...) from exc` when a
translation adds domain context; use a bare `raise` when the same exception
continues.

Do not catch `Exception` inside ordinary domain code. A process, task, or
request boundary may catch it to report an otherwise unhandled failure, but it
must keep the traceback, run the required cleanup, and return or raise an
explicit outcome.

Never use a bare `except`, swallow an error with `pass`, or return a sentinel
the signature does not declare. Keep error messages actionable and free of
credentials, personal data, and raw external payloads.

Use context managers or `finally` for cleanup. A cleanup failure must not
quietly replace the original cause; combine, chain, or report it as the
project's policy says.

## Map failures at the FastAPI boundary

Keep each feature's domain exception types under `domain/failures/` and export
only the ones another feature may handle. Install their HTTP mappings once
through registered exception handlers in `app/app.py`. Keep `HTTPException` in
presentation and dependency providers for transport-local failures; never make
application, domain, or infrastructure code import FastAPI to report a status.

Choose validation and domain status codes from the existing API contract.
FastAPI's default validation status is not permission to change a service that
deliberately standardized another one. Assert one exact status in tests rather
than accepting several.

## Keep the envelope safe

- Return one documented error shape with stable machine-readable meaning.
- Distinguish authentication, authorization, absence, conflict, invalid input,
  throttling, and unavailable dependencies when callers can act differently.
- Never return tracebacks, SQL, internal class names, credentials, or raw
  upstream payloads.

Send an unexpected exception to the application's outer error capture and return
the stable 500 envelope. Keep the request correlation on the captured event and
out of the public body.

An exception handler takes the exact exception type and returns a declared
`Response`. Middleware that observes the result must not replace its status,
headers, or body by accident.

Finish when each failure has one owner, callers can tell every promised outcome
apart, the original cause stays available for diagnosis, every promised failure
maps once to an exact status and body, and unexpected failures keep their
diagnostic context without exposing it to callers.
