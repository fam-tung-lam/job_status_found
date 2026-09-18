"""The `auth_events` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped

from job_status_found.db.db import Base, IpAddress, JsonObject, SurrogateKey


class AuthEventTable(Base):
    """One security event, kept for audit and read by the sign-in throttle.

    The row outlives its user: deleting the user only clears `user_id`.
    """

    __tablename__ = "auth_events"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        Index(
            "ix_auth_events_identifier_hash_event_type_created_at",
            "identifier_hash",
            "event_type",
            "created_at",
        ),
        Index(
            "ix_auth_events_ip_address_event_type_created_at",
            "ip_address",
            "event_type",
            "created_at",
        ),
        Index("ix_auth_events_user_id_created_at", "user_id", "created_at"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    user_id: Mapped[UUID | None]
    """The subject; null before sign-in and after account deletion."""

    event_type: Mapped[str]
    """What happened, such as `sign_in_failed` or `refresh_token_reused`."""

    identifier_hash: Mapped[bytes | None]
    """HMAC-SHA-256 of the normalized email, so attempts group without the address."""

    ip_address: Mapped[IpAddress | None]
    """Client IP address."""

    user_agent: Mapped[str | None]
    """Client user agent."""

    details: Mapped[JsonObject | None]
    """Event-specific facts; never a secret, code, or raw email."""

    created_at: Mapped[datetime]
    """When the event happened."""
