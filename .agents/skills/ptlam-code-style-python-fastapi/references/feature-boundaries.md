# FastAPI Feature Boundaries

Each feature publishes one surface through its package `__init__.py`. Another
feature may import an exported use case, application DTO, domain entity, or
domain failure. It never reaches into the target's `di.py`, presentation, or
infrastructure layers.

```python
# features/billing/application/use_cases/charge_customer.py
from myapp.features.users import GetUser, UserNotFound  # public facade
```

An export is a compatibility promise. Export only a symbol with a real external
consumer, and keep importing the package free of connection, registration, and
other runtime side effects.

## Enforce the dependency graph

Use the repository's existing architecture checker. For a new service, add
[Import Linter](https://import-linter.readthedocs.io/en/stable/) and adapt this
verified TOML template to the real package and features:

```toml
[tool.importlinter]
root_package = "myapp"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Application and independent features depend inward"
type = "layers"
layers = [
    "myapp.app.app",
    "myapp.features.users | myapp.features.billing | myapp.features.orders",
    "myapp.shared | myapp.integrations",
]

[[tool.importlinter.contracts]]
name = "Presentation enters through application"
type = "forbidden"
source_modules = [
    "myapp.features.users.presentation",
    "myapp.features.billing.presentation",
    "myapp.features.orders.presentation",
]
forbidden_modules = [
    "myapp.app.db",
    "myapp.features.users.infrastructure",
    "myapp.features.billing.infrastructure",
    "myapp.features.orders.infrastructure",
    "myapp.integrations",
    "sqlalchemy",
]
allow_indirect_imports = true

[[tool.importlinter.contracts]]
name = "Application stays transport and infrastructure neutral"
type = "forbidden"
source_modules = [
    "myapp.features.users.application",
    "myapp.features.billing.application",
    "myapp.features.orders.application",
]
forbidden_modules = [
    "myapp.app.db",
    "myapp.integrations",
    "myapp.features.users.infrastructure",
    "myapp.features.billing.infrastructure",
    "myapp.features.orders.infrastructure",
    "myapp.features.users.presentation",
    "myapp.features.billing.presentation",
    "myapp.features.orders.presentation",
    "fastapi",
    "starlette",
    "sqlalchemy",
]
allow_indirect_imports = true

[[tool.importlinter.contracts]]
name = "Domain is the innermost layer"
type = "forbidden"
source_modules = [
    "myapp.features.users.domain",
    "myapp.features.billing.domain",
    "myapp.features.orders.domain",
]
forbidden_modules = [
    "myapp.app.db",
    "myapp.integrations",
    "myapp.features.users.application",
    "myapp.features.billing.application",
    "myapp.features.orders.application",
    "myapp.features.users.infrastructure",
    "myapp.features.billing.infrastructure",
    "myapp.features.orders.infrastructure",
    "myapp.features.users.presentation",
    "myapp.features.billing.presentation",
    "myapp.features.orders.presentation",
    "fastapi",
    "starlette",
    "pydantic",
    "sqlalchemy",
]
allow_indirect_imports = true
```

The top layer is the composition root, `myapp.app.app`, rather than the whole
`app/` package, because feature infrastructure imports `app/db.py`. Run
`lint-imports` in CI. The external-package flag is required when a contract
names SQLAlchemy, FastAPI, Starlette, or Pydantic. Allow indirect imports in a
forbidden contract when only direct bypasses are invalid and the valid path
reaches that package through a lower layer.

Independent features coordinate in `app/app.py` or through events. When one
caller must invoke another feature's facade, ignore only that exact facade
import in the independent-sibling layer and add a forbidden contract that still
blocks the target's `di.py`, presentation, and infrastructure internals. Record
the exception as owned design debt.

## Break cycles at the boundary

Use string targets for SQLAlchemy relationships across infrastructure models and
one shared declarative base. Put annotation-only imports behind `TYPE_CHECKING`
under the active annotation policy. Map related rows to domain entities inside
the owning infrastructure adapter.

If a cycle survives both repairs, move a genuinely cross-cutting domain concept
into `shared/` or merge the features. The boundary is wrong; an import trick
does not repair it.

Finish when every cross-feature import enters a facade, presentation does not
bypass application, application depends on ports rather than infrastructure,
domain imports no outer layer, the configured graph passes, and no ignored edge
hides an unowned dependency.
