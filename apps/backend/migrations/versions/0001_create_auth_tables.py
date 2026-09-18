"""Create the eight tables of the auth feature.

Revision ID: 0001
Revises:
Create Date: 2026-09-18 22:12:34.104634
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply this revision."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("email_normalized", sa.Text(), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("locale", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("terms_version", sa.Text(), nullable=False),
        sa.Column("terms_accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('user', 'admin')", name=op.f("ck_users_role_vocabulary")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email_normalized", name=op.f("uq_users_email_normalized")),
    )
    op.create_table(
        "auth_events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("identifier_hash", sa.LargeBinary(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_auth_events_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_events")),
    )
    op.create_index(
        "ix_auth_events_identifier_hash_event_type_created_at",
        "auth_events",
        ["identifier_hash", "event_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_events_ip_address_event_type_created_at",
        "auth_events",
        ["ip_address", "event_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_events_user_id_created_at", "auth_events", ["user_id", "created_at"], unique=False
    )
    op.create_table(
        "email_challenges",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("secret_hash", sa.LargeBinary(), nullable=False),
        sa.Column("new_email", sa.Text(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "purpose IN ('verify_email', 'reset_password', 'change_email')",
            name=op.f("ck_email_challenges_purpose_vocabulary"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_email_challenges_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_email_challenges")),
    )
    op.create_index(
        op.f("ix_email_challenges_secret_hash"), "email_challenges", ["secret_hash"], unique=False
    )
    op.create_index(
        "uq_email_challenges_unconsumed_user_id_purpose",
        "email_challenges",
        ["user_id", "purpose"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL"),
    )
    op.create_table(
        "external_identities",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("provider_subject", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_signed_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "provider IN ('google')", name=op.f("ck_external_identities_provider_vocabulary")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_external_identities_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_identities")),
        sa.UniqueConstraint(
            "provider",
            "provider_subject",
            name=op.f("uq_external_identities_provider_provider_subject"),
        ),
        sa.UniqueConstraint(
            "user_id", "provider", name=op.f("uq_external_identities_user_id_provider")
        ),
    )
    op.create_table(
        "oauth_authorization_attempts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("client_kind", sa.Text(), nullable=False),
        sa.Column("state_hash", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.Text(), nullable=False),
        sa.Column("provider_code_verifier", sa.Text(), nullable=True),
        sa.Column("client_redirect_uri", sa.Text(), nullable=False),
        sa.Column("client_code_challenge", sa.Text(), nullable=False),
        sa.Column("initiating_user_id", sa.Uuid(), nullable=True),
        sa.Column("resolved_user_id", sa.Uuid(), nullable=True),
        sa.Column("exchange_code_hash", sa.LargeBinary(), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "client_kind IN ('web', 'ios', 'android')",
            name=op.f("ck_oauth_authorization_attempts_client_kind_vocabulary"),
        ),
        sa.CheckConstraint(
            "provider IN ('google')",
            name=op.f("ck_oauth_authorization_attempts_provider_vocabulary"),
        ),
        sa.CheckConstraint(
            "purpose IN ('sign_in', 'link', 'reauthenticate')",
            name=op.f("ck_oauth_authorization_attempts_purpose_vocabulary"),
        ),
        sa.ForeignKeyConstraint(
            ["initiating_user_id"],
            ["users.id"],
            name=op.f("fk_oauth_authorization_attempts_initiating_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_user_id"],
            ["users.id"],
            name=op.f("fk_oauth_authorization_attempts_resolved_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_oauth_authorization_attempts")),
        sa.UniqueConstraint(
            "exchange_code_hash", name=op.f("uq_oauth_authorization_attempts_exchange_code_hash")
        ),
        sa.UniqueConstraint("state_hash", name=op.f("uq_oauth_authorization_attempts_state_hash")),
    )
    op.create_table(
        "password_credentials",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_password_credentials_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_password_credentials")),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("sign_in_method", sa.Text(), nullable=False),
        sa.Column("client_kind", sa.Text(), nullable=False),
        sa.Column("is_persistent", sa.Boolean(), nullable=False),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("authenticated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "client_kind IN ('web', 'ios', 'android')",
            name=op.f("ck_sessions_client_kind_vocabulary"),
        ),
        sa.CheckConstraint(
            "revocation_reason IN ('signed_out', 'revoked_by_user', 'password_changed', "
            "'refresh_token_reused', 'account_suspended', 'account_deleted')",
            name=op.f("ck_sessions_revocation_reason_vocabulary"),
        ),
        sa.CheckConstraint(
            "sign_in_method IN ('password', 'google')",
            name=op.f("ck_sessions_sign_in_method_vocabulary"),
        ),
        sa.CheckConstraint(
            "(revoked_at IS NULL) = (revocation_reason IS NULL)",
            name=op.f("ck_sessions_revocation_reason_with_revoked_at"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_sessions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("parent_token_id", sa.Uuid(), nullable=True),
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_token_id"],
            ["refresh_tokens.id"],
            name=op.f("fk_refresh_tokens_parent_token_id_refresh_tokens"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_refresh_tokens_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_refresh_tokens_token_hash")),
    )
    op.create_index(
        "ix_refresh_tokens_parent_token_id", "refresh_tokens", ["parent_token_id"], unique=False
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"], unique=False)


def downgrade() -> None:
    """Revert this revision."""
    op.drop_index("ix_refresh_tokens_session_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_parent_token_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("password_credentials")
    op.drop_table("oauth_authorization_attempts")
    op.drop_table("external_identities")
    op.drop_index(
        "uq_email_challenges_unconsumed_user_id_purpose",
        table_name="email_challenges",
        postgresql_where=sa.text("consumed_at IS NULL"),
    )
    op.drop_index(op.f("ix_email_challenges_secret_hash"), table_name="email_challenges")
    op.drop_table("email_challenges")
    op.drop_index("ix_auth_events_user_id_created_at", table_name="auth_events")
    op.drop_index("ix_auth_events_ip_address_event_type_created_at", table_name="auth_events")
    op.drop_index("ix_auth_events_identifier_hash_event_type_created_at", table_name="auth_events")
    op.drop_table("auth_events")
    op.drop_table("users")
