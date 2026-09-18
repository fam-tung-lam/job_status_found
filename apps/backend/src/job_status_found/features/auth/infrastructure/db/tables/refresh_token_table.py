"""The `refresh_tokens` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped

from job_status_found.db.db import Base, SurrogateKey


class RefreshTokenTable(Base):
    """One refresh token in a session's rotation family.

    Only the token's hash is stored. Presenting a token that is already used or
    revoked revokes the whole session.
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        # The ERD leaves these two delete rules open. The purge deletes a session
        # 30 days after it ends and a token 1 day after it expires, so a session
        # takes its tokens with it, and an expired parent can go before its child.
        ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["parent_token_id"], ["refresh_tokens.id"], ondelete="SET NULL"),
        UniqueConstraint("token_hash"),
        # Serve revoking a session's tokens, finding a token's child, and the
        # two delete rules above, which PostgreSQL runs once per deleted row.
        Index("ix_refresh_tokens_session_id", "session_id"),
        Index("ix_refresh_tokens_parent_token_id", "parent_token_id"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    session_id: Mapped[UUID]
    """The session this token keeps alive."""

    parent_token_id: Mapped[UUID | None]
    """The token this one replaced; null for a session's first token."""

    token_hash: Mapped[bytes]
    """SHA-256 of the 256-bit random token."""

    created_at: Mapped[datetime]
    """When the token was issued."""

    expires_at: Mapped[datetime]
    """Copied from the session's idle expiry at issue."""

    used_at: Mapped[datetime | None]
    """When the token was exchanged for its child."""

    revoked_at: Mapped[datetime | None]
    """When the token was superseded or its session ended."""
