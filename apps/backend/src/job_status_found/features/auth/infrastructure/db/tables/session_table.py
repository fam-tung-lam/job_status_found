"""The `sessions` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped

from job_status_found.features.core import Base, IpAddress, SurrogateKey


class SessionTable(Base):
    """One sign-in on one device, which its refresh tokens keep alive."""

    __tablename__ = "sessions"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        CheckConstraint(
            "sign_in_method IN ('password', 'google')", name="sign_in_method_vocabulary"
        ),
        CheckConstraint("client_kind IN ('web', 'ios', 'android')", name="client_kind_vocabulary"),
        CheckConstraint(
            "revocation_reason IN ('signed_out', 'revoked_by_user', 'password_changed', "
            "'refresh_token_reused', 'account_suspended', 'account_deleted')",
            name="revocation_reason_vocabulary",
        ),
        CheckConstraint(
            "(revoked_at IS NULL) = (revocation_reason IS NULL)",
            name="revocation_reason_with_revoked_at",
        ),
        # Serves the session list, the revoke-all operations, and the cascade
        # from `users`.
        Index("ix_sessions_user_id", "user_id"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; the `sid` claim of every access token of this session."""

    user_id: Mapped[UUID]
    """The signed-in user."""

    sign_in_method: Mapped[str]
    """How the user signed in: `password` or `google`."""

    client_kind: Mapped[str]
    """`web`, `ios`, or `android`; fixes how the refresh token is delivered."""

    is_persistent: Mapped[bool]
    """Whether the user chose "Remember this device"."""

    ip_address: Mapped[IpAddress | None]
    """Client IP address at sign-in."""

    user_agent: Mapped[str | None]
    """Client user agent at sign-in, truncated to 512 characters."""

    created_at: Mapped[datetime]
    """When the user signed in."""

    authenticated_at: Mapped[datetime]
    """Last credential proof; gates sensitive operations."""

    last_refreshed_at: Mapped[datetime]
    """When a refresh token of this session was last exchanged."""

    idle_expires_at: Mapped[datetime]
    """When the session ends without a refresh; slides forward on every refresh."""

    absolute_expires_at: Mapped[datetime]
    """When the session ends regardless of refreshes; never moves."""

    revoked_at: Mapped[datetime | None]
    """When the session was revoked."""

    revocation_reason: Mapped[str | None]
    """Why the session was revoked; set exactly when `revoked_at` is set."""
