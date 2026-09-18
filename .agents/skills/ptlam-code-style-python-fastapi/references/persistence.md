# FastAPI Persistence Registration

Feature-owned SQLAlchemy models and one explicit Alembic metadata module make
autogeneration complete while domain entities remain persistence-independent.

## Keep persistence models in infrastructure

Put one primary mapped table per file under
`features/<feature>/infrastructure/persistence/models/`, together with its
association tables and persistence-owned enums. Re-export every mapped table
from that package's `__init__.py` so importing it registers the complete
feature.

```python
# features/users/infrastructure/persistence/models/__init__.py
from myapp.features.users.infrastructure.persistence.models.profile_table import (
    ProfileTable,
)
from myapp.features.users.infrastructure.persistence.models.user_table import UserTable

__all__ = ["ProfileTable", "UserTable"]
```

These mapped classes are infrastructure records, not domain entities. An
`infrastructure/adapters/` repository maps them to and from types under
`domain/entities/` before returning through an application port.

Keep a closed string vocabulary that belongs to a domain concept under
`domain/`, using `enum.StrEnum` when its mechanics fit. Keep a database-only
enum beside its mapped table and translate it at the adapter boundary.

## Keep one Alembic metadata module

For one database, keep one root `alembic.ini`, one `migrations/env.py`, and one
revision history. `app/alembic_metadata.py` is the explicit exception to the
facade rule: it imports every feature's persistence-model package solely to
populate the shared declarative base. The concrete name says why the imports
exist; `registry.py` does not.

```python
# myapp/app/alembic_metadata.py
"""Import every feature's persistence models so Base.metadata is complete."""
from myapp.app.db import Base
from myapp.features.billing.infrastructure.persistence import (
    models as _billing,  # noqa: F401
)
from myapp.features.users.infrastructure.persistence import models as _users  # noqa: F401

metadata = Base.metadata
```

```python
# migrations/env.py
from myapp.app.alembic_metadata import metadata as target_metadata
```

Tables remain feature-owned; migrations describe the whole database. Preserve an
established multi-database layout instead of forcing it into one history.

## Verify the published schema

Test the metadata that Alembic consumes against an independently agreed schema.
Run this test in a fresh Python process before other tests import mapped models;
a shared process can hide a missing registration import. For an illustrative
schema with three tables, a unique email, and a profile-to-user relation:

```python
from sqlalchemy import UniqueConstraint


def test_alembic_metadata_exposes_the_agreed_schema() -> None:
    # Given: schema expectations come from the agreed persistence contract.
    expected_tables = {"billing_accounts", "profiles", "users"}
    expected_user_key = {"id"}
    expected_user_uniques = {("email",)}
    expected_profile_references = {("user_id", "users.id")}

    # When: Alembic loads the public metadata entry point.
    from myapp.app.alembic_metadata import metadata

    # Then: the declared tables and constraints are available to Alembic.
    assert set(metadata.tables) == expected_tables
    users = metadata.tables["users"]
    profiles = metadata.tables["profiles"]
    assert {column.name for column in users.primary_key} == expected_user_key
    assert {
        tuple(column.name for column in constraint.columns)
        for constraint in users.constraints
        if isinstance(constraint, UniqueConstraint)
    } == expected_user_uniques
    assert {
        (key.parent.name, key.target_fullname) for key in profiles.foreign_keys
    } == expected_profile_references
```

Adapt the literal expectations to the real schema, including schema-qualified
table keys when used. Never derive expected tables or constraints from the
registry, model files, or metadata under test. Import-boundary checks are
separate architecture checks; import presence does not prove registration.

## Compare without creating a revision

With Alembic 1.9 or newer, `alembic check` runs autogenerate comparison without
saving a revision. Use it only with an existing permitted test database and an
inspected `env.py`: loading that file can have side effects. It retains
Alembic's detection limits, so a clean result does not prove every schema
detail. If the installed version or environment cannot run it safely, report the
gap.

Creating or applying migrations is change-mode work. Use
`alembic revision --autogenerate` only when a revision is needed for the
requested change, then inspect its operations before applying it.

Finish when domain entities import no SQLAlchemy mechanic, feature
infrastructure owns each mapped table, the isolated metadata contract test
passes, and the permitted schema comparison shows no unintended operations or
has a reported verification gap.
