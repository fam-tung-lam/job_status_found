"""A security event about to be stored."""

from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.core import JsonObject


@dataclass(frozen=True, slots=True)
class NewAuthEvent:
    """The non-secret facts of one security-relevant event."""

    event_type: AuthEventType
    """What happened."""

    occurred_at: datetime
    """When it happened."""

    owner_id: UUID | None = None
    """The affected account, when one is known."""

    identifier_hash: bytes | None = None
    """The keyed normalized-email hash, never the email itself."""

    ip_address: IPv4Address | IPv6Address | None = None
    """The request's client address, when available."""

    user_agent: str | None = None
    """The request's user agent, truncated to 512 characters."""

    details: JsonObject | None = None
    """Event-specific facts that contain no credentials or raw identifiers."""
