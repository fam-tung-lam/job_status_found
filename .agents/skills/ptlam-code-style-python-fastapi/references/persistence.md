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

## Declare columns without assigning `Any`

`mapped_column()` returns `MappedColumn[Any]`, so `name: Mapped[str] =
mapped_column(...)` assigns `Any` to a typed attribute. A checker that rejects
unsound assignments, such as ty's `unsound-assignment`, flags every such
column. Where the project's checker enables that rule, declare each column by
its annotation alone:

- Let the declarative base's `type_annotation_map` pick every column type,
  including a PEP 695 alias or `NewType` for a special type such as `inet`.
- Put a reusable column configuration, such as a database-generated primary
  key, in an `Annotated[T, mapped_column(...)]` alias and annotate the column
  as `Mapped[Alias]`.
- Declare primary keys, foreign keys, unique rules, `CHECK` constraints, and
  indexes as table-level constructs in `__table_args__`.

```python
type SurrogateKey = Annotated[
    UUID, mapped_column(primary_key=True, server_default=text("uuidv7()"))
]


class ProfileTable(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        UniqueConstraint("user_id"),
    )

    id: Mapped[SurrogateKey]
    user_id: Mapped[UUID]
    bio: Mapped[str | None]
```

Never silence the rule with a cast, an ignore comment, or a per-directory
override.

## Verify migrations, not declarations

Never write a test that restates the agreed schema or inspects SQLAlchemy
metadata. It copies the specification, needs a second edit for every schema
change, and catches nothing the checks below miss.

- Run `alembic check` against a database at head as its own command in the
  project's checks. It runs in a fresh process, so it fails when the Alembic
  metadata module never imports a feature's persistence models, and when the
  mapped tables and the revisions drift apart. Use it only with a permitted
  database and an inspected `env.py`: loading that file can have side effects.
- Configure the comparison in `env.py` with `compare_server_default=True` and,
  on Alembic 1.19.2 or newer, the opt-in `alembic.ext.checkconstraint_byname`
  autogenerate plugin, which reports added or removed `CHECK` constraints by
  name. Autogenerate never compares a `CHECK` constraint's text, a primary key,
  or a partial index's condition, so read those in every revision.
- Test each revision against a throwaway database on the production engine:
  upgrade from empty, then run `alembic check` through `env.py`; downgrade to
  base; and exercise the rules only the database enforces, such as `CHECK`
  constraints, foreign-key actions, primary keys, and unique or partial
  indexes. Reuse the project's migration command inside the test instead of a
  second copy of the comparison options.

Creating or applying migrations is change-mode work. Use
`alembic revision --autogenerate` only when a revision is needed for the
requested change, then inspect its operations before applying it.

Finish when domain entities import no SQLAlchemy mechanic, feature
infrastructure owns each mapped table, `alembic check` passes against a
database at head, and the revision tests pass or the verification gap is
reported.
