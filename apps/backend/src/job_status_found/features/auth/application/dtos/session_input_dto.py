"""Request metadata and choices used to open a session."""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind


@dataclass(frozen=True, slots=True)
class SessionInputDTO:
    """The client choices and request facts stored with a new session."""

    client_kind: ClientKind
    """The client platform and refresh-token channel."""

    remember_me: bool
    """Whether the session gets the persistent lifetimes."""

    ip_address: IPv4Address | IPv6Address | None
    """The request's client address when one is available."""

    user_agent: str | None
    """The request's user-agent string, already truncated to 512 characters."""
