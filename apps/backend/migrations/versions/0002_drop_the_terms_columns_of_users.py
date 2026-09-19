"""Drop the terms columns of users until terms acceptance returns in the last MVP change.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-19 11:29:31.836707
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UNKNOWN_TERMS_VERSION = "unknown"
"""`terms_version` a downgrade gives existing rows, whose accepted version was never stored."""


def upgrade() -> None:
    """Apply this revision."""
    op.drop_column("users", "terms_accepted_at")
    op.drop_column("users", "terms_version")


def downgrade() -> None:
    """Revert this revision, filling the restored columns of existing rows."""
    # Add both columns as nullable, so existing rows can take them.
    op.add_column("users", sa.Column("terms_version", sa.Text(), nullable=True))
    op.add_column(
        "users", sa.Column("terms_accepted_at", sa.DateTime(timezone=True), nullable=True)
    )

    # Fill existing rows: no version was stored, and sign-up was the acceptance.
    op.execute(
        sa.text(
            "UPDATE users SET terms_version = :unknown_version, terms_accepted_at = created_at"
        ).bindparams(unknown_version=_UNKNOWN_TERMS_VERSION)
    )

    # Restore the constraints revision 0001 created.
    op.alter_column("users", "terms_version", nullable=False)
    op.alter_column("users", "terms_accepted_at", nullable=False)
