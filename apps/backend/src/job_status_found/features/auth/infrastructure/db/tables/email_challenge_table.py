"""The `email_challenges` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, text
from sqlalchemy.orm import Mapped

from job_status_found.db.db import Base, SurrogateKey


class EmailChallengeTable(Base):
    """One emailed code or link a user must answer to prove a mailbox.

    At most one challenge per user and purpose is unconsumed at a time.
    """

    __tablename__ = "email_challenges"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        CheckConstraint(
            "purpose IN ('verify_email', 'reset_password', 'change_email')",
            name="purpose_vocabulary",
        ),
        Index(
            "uq_email_challenges_unconsumed_user_id_purpose",
            "user_id",
            "purpose",
            unique=True,
            postgresql_where=text("consumed_at IS NULL"),
        ),
        # Finds the challenge of a reset link, which carries no user id.
        Index("ix_email_challenges_secret_hash", "secret_hash"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    user_id: Mapped[UUID]
    """The user who must answer."""

    purpose: Mapped[str]
    """`verify_email`, `reset_password`, or `change_email`."""

    secret_hash: Mapped[bytes]
    """HMAC-SHA-256 of the code or link token."""

    new_email: Mapped[str | None]
    """The requested address; only for `change_email`."""

    attempt_count: Mapped[int]
    """Wrong answers so far."""

    created_at: Mapped[datetime]
    """When the challenge was sent."""

    expires_at: Mapped[datetime]
    """When the code or link stops working."""

    consumed_at: Mapped[datetime | None]
    """When the challenge was answered or used up."""
