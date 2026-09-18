# FastAPI Request Pipeline

The default layered path for a new feature-first service. Keep a coherent
existing architecture, but never add a second request path inside it.

```text
presentation adapter -> application DTO -> use case -> application port -> infrastructure adapter
```

Every request follows this path. A presentation adapter imports no repository
adapter, session, SQLAlchemy model, or integration client. Application and
domain code import no infrastructure or FastAPI mechanic. Reads and writes use
the same lane, including a read whose use case only turns absence into a domain
failure.

The short use cases that simple reads need are the deliberate price of a
predictable boundary. Do not add a direct read path that future handlers must
tell apart from the write path.

## Give each layer one responsibility

| Layer                  | Owns                                                         | Does not own                                          |
| ---------------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| Presentation           | HTTP or task input, auth context, status, and output mapping | Policy, queries, or transaction decisions             |
| Application DTO        | Validated operation input and output                         | `Request`, `Depends`, writes, or orchestration        |
| Use case               | One operation, its orchestration, and its transaction        | FastAPI, SQLAlchemy, or transport errors              |
| Domain                 | Business entities, values, rules, and stable failures        | FastAPI, Pydantic transport, or persistence mechanics |
| Application port       | One persistence or remote-effect contract                    | Transport DTOs, HTTP errors, or commit policy         |
| Infrastructure adapter | Implements a port with database or vendor mechanics          | Presentation mapping or business policy               |
| Feature `di.py`        | FastAPI dependency providers and feature assembly            | Business policy                                       |

Dependency injection assembles the path at the feature root. Convert transport,
persistence, vendor, and domain values where their meaning changes. FastAPI
types stop at presentation and `di.py`; SQLAlchemy and client types stay in
infrastructure.

## Check the pipeline mechanically

Search changed presentation files for infrastructure, session, SQLAlchemy, and
integration imports. Search `application/` and `domain/` for FastAPI, Starlette,
SQLAlchemy, and feature-infrastructure imports. Search presentation adapters for
commits, and infrastructure adapters for hidden commits. Remove each result, or
identify it as untouched legacy code outside the change.

Finish when every changed entry point calls one use case, each use case owns one
transaction decision, application depends on ports rather than adapters,
infrastructure implements those ports, and no inner layer imports its caller.
