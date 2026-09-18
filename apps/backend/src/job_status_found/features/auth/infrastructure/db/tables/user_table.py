"""The `users` table."""

from datetime import datetime

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped

from job_status_found.db.db import Base, SurrogateKey


class UserTable(Base):
    """One account, whose identity is its normalized email address."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email_normalized"),
        CheckConstraint("role IN ('user', 'admin')", name="role_vocabulary"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    email: Mapped[str]
    """The address as the user typed it; used for display and delivery."""

    email_normalized: Mapped[str]
    """NFKC, lower-case form of `email`; the identity of the mailbox."""

    email_verified_at: Mapped[datetime | None]
    """When the user proved control of the mailbox; null while unverified."""

    first_name: Mapped[str | None]
    """Given name; null when a provider omits it."""

    last_name: Mapped[str | None]
    """Family name; null when a provider omits it."""

    avatar_url: Mapped[str | None]
    """Picture URL copied from the provider's `picture` claim."""

    locale: Mapped[str | None]
    """Preferred language as a BCP 47 tag."""

    role: Mapped[str]
    """Instance-level role: `user` or `admin`."""

    terms_version: Mapped[str]
    """Version of the terms the user accepted at sign-up."""

    terms_accepted_at: Mapped[datetime]
    """When the user accepted those terms."""

    suspended_at: Mapped[datetime | None]
    """When the account was suspended; while set, sign-in and refresh fail."""

    deletion_requested_at: Mapped[datetime | None]
    """When the user asked for deletion; while set, sign-in fails until the purge."""

    created_at: Mapped[datetime]
    """When the account was created."""

    updated_at: Mapped[datetime]
    """When the row last changed."""
