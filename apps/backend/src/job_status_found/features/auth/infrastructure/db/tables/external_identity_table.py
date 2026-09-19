"""The `external_identities` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped

from job_status_found.features.core import Base, SurrogateKey


class ExternalIdentityTable(Base):
    """One provider account linked to a user.

    `(provider, provider_subject)` finds the returning user, and
    `(user_id, provider)` keeps one identity per provider per user.
    """

    __tablename__ = "external_identities"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        UniqueConstraint("provider", "provider_subject"),
        UniqueConstraint("user_id", "provider"),
        CheckConstraint("provider IN ('google')", name="provider_vocabulary"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    user_id: Mapped[UUID]
    """The user this identity signs in."""

    provider: Mapped[str]
    """The identity provider; `google` for now."""

    provider_subject: Mapped[str]
    """The provider's `sub` claim; never the email, which can change."""

    email: Mapped[str | None]
    """The address the provider last asserted."""

    email_verified: Mapped[bool]
    """Whether the provider claimed the email verified at the last sign-in."""

    created_at: Mapped[datetime]
    """When the identity was linked."""

    last_signed_in_at: Mapped[datetime | None]
    """When the user last signed in through this identity."""
