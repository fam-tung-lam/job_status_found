"""The `password_credentials` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from job_status_found.db.db import Base


class PasswordCredentialTable(Base):
    """The password of one user; a social-only user has no row."""

    __tablename__ = "password_credentials"
    __table_args__ = (
        PrimaryKeyConstraint("user_id"),
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    user_id: Mapped[UUID]
    """The user this password signs in; also the row's key."""

    password_hash: Mapped[str]
    """Argon2id PHC string, including its parameters."""

    created_at: Mapped[datetime]
    """When the user first set a password."""

    updated_at: Mapped[datetime]
    """When the password last changed."""
