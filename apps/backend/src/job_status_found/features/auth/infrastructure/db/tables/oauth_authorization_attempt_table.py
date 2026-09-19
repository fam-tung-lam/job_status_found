"""The `oauth_authorization_attempts` table."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped

from job_status_found.features.core import Base, SurrogateKey


class OAuthAuthorizationAttemptTable(Base):
    """One browser sign-in through a provider, from start to code redemption.

    The row passes through `created_at`, `provider_returned_at`, and
    `consumed_at`. Each step requires the previous instant set and its own
    null, which makes every `state` and exchange code single-use.
    """

    __tablename__ = "oauth_authorization_attempts"
    __table_args__ = (
        ForeignKeyConstraint(["initiating_user_id"], ["users.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["resolved_user_id"], ["users.id"], ondelete="CASCADE"),
        UniqueConstraint("state_hash"),
        UniqueConstraint("exchange_code_hash"),
        CheckConstraint("provider IN ('google')", name="provider_vocabulary"),
        CheckConstraint(
            "purpose IN ('sign_in', 'link', 'reauthenticate')", name="purpose_vocabulary"
        ),
        CheckConstraint("client_kind IN ('web', 'ios', 'android')", name="client_kind_vocabulary"),
    )

    id: Mapped[SurrogateKey]
    """Surrogate key; `uuidv7()` makes keys sort by creation time."""

    provider: Mapped[str]
    """The identity provider; `google` for now."""

    purpose: Mapped[str]
    """`sign_in`, `link`, or `reauthenticate`."""

    client_kind: Mapped[str]
    """`web`, `ios`, or `android`."""

    state_hash: Mapped[bytes]
    """SHA-256 of the `state` sent to the provider."""

    nonce: Mapped[str]
    """Must come back inside the ID token; stored in the clear, useless alone."""

    provider_code_verifier: Mapped[str | None]
    """PKCE verifier toward the provider; stored in the clear, useless alone."""

    client_redirect_uri: Mapped[str]
    """The allow-listed app callback."""

    client_code_challenge: Mapped[str]
    """PKCE S256 challenge from the app."""

    initiating_user_id: Mapped[UUID | None]
    """The signed-in user; required for `link` and `reauthenticate`."""

    resolved_user_id: Mapped[UUID | None]
    """The user the provider identity resolved to, set when the provider returns."""

    exchange_code_hash: Mapped[bytes | None]
    """SHA-256 of the one-time code the app redeems."""

    failure_code: Mapped[str | None]
    """Why the attempt failed; set instead of `resolved_user_id`."""

    created_at: Mapped[datetime]
    """When the app started the attempt."""

    expires_at: Mapped[datetime]
    """When the attempt stops working."""

    provider_returned_at: Mapped[datetime | None]
    """When the provider redirected back to the callback."""

    consumed_at: Mapped[datetime | None]
    """When the app redeemed the exchange code."""
