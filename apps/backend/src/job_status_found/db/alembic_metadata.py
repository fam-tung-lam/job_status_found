"""The complete schema Alembic compares and migrates.

Importing a feature's tables package registers its tables on `Base.metadata`.
This module is the one place outside a feature that imports those packages,
and it publishes each one beside the metadata it fills. Add every new
feature's tables package to the imports and to `__all__`.
"""

from job_status_found.db.db import Base
from job_status_found.features.auth.infrastructure.db import tables as auth_tables

__all__ = ["auth_tables", "metadata"]

metadata = Base.metadata
"""Metadata holding every feature's mapped tables."""
