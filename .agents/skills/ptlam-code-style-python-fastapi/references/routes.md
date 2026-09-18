# FastAPI Routes and HTTP Contracts

The typed HTTP surface: canonical paths, request data, response data, status,
and OpenAPI metadata.

## Compose the URL once

Start a feature's cohesive HTTP surface with one `APIRouter` in
`presentation/http/<resource>_controller.py`, named as
[file-organization.md](file-organization.md) requires. Related handlers may stay
together; split independently owned resources into router modules, each with its
own resource name, and compose them with `include_router`. The feature HTTP
router may assemble those routers without holding their handlers. Do not create
one file for every endpoint merely to count fewer functions.

Add `presentation/http/v1.py`, `v2.py`, and later version composition only when
a second public version exists. Declare each shared prefix and tag either on a
router or where its parent includes it, never at both levels. Attach the API
version once near the application boundary.

For the root operation of an already-prefixed router, use `""` unless the
contract intentionally includes a trailing slash. Test canonical paths with
redirect following disabled so an accidental 307 does not pass unnoticed.

## Make the signature the contract

- Type every path, query, header, cookie, and body parameter.
- Use `Annotated` with `Path`, `Query`, `Header`, or `Body` when the transport
  needs constraints, aliases, or documentation beyond the Python type.
- Group related query fields in a Pydantic query model when the installed
  FastAPI version supports that binding.
- Declare the response through a precise return type or `response_model`. Use
  `response_model` when the runtime object differs from the public DTO. Never
  expose an ORM object or an internal field by accident.
- Set a non-default success status with `fastapi.status`. A 204 carries no body.
- Reuse the API's stable error model and declare each promised non-success
  status and body with `responses=` or the repository's central OpenAPI
  customization. Raising `HTTPException` alone does not document that shape.
- Attach one realistic payload to each request and response DTO through
  `model_config` `json_schema_extra` or `openapi_examples`, so the generated
  documentation shows a concrete example.

FastAPI validates, documents, serializes, and filters a declared response. The
[response model guide](https://fastapi.tiangolo.com/tutorial/response-model/)
identifies the feature; it is not required reading. When behavior differs, read
the locked packages and assert the local response and OpenAPI contract.

Read raw request bytes only when the protocol needs the exact bytes, such as a
signed webhook. Authenticate the raw body before parsing it, and document why
normal typed-body validation is deferred.

## Bound every collection operation

Give a list endpoint an explicit page size with a default and a maximum, a
deterministic sort, and the filters the caller actually needs. Return the paging
state the client needs for the next page.

Add these when the endpoint is created. Retrofitting paging onto a published
`GET /items` that returned everything breaks every consumer that depends on the
full list.

## Make a repeated write safe

A mobile client, a proxy, or an operator will send the same write twice. Accept
an idempotency key, or derive one from the operation's natural key, and return
the original result for the repeat instead of creating a second row, charge, or
message. Declare the key in the signature like any other input, and record which
operations promise it in the API contract.

## Delegate one operation

A handler parses transport input, calls one injected use case, and shapes the
declared response. It imports no repository, session, SQLAlchemy object, or
integration client. Map a multi-field body to an application DTO or command;
pass a single path or query value directly when that is the whole input.

Finish when the canonical URL does not redirect, input and output DTOs hide
internal data, every collection response is paged and ordered, a repeated write
produces one effect, and OpenAPI records the intended status and error contract.
