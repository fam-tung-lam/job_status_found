"""Build application session input from a version 1 HTTP request."""

from ipaddress import ip_address

from fastapi import Request

from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind

_MAX_USER_AGENT_LENGTH = 512
"""Most user-agent characters stored on a session or audit event."""


def build_session_input_from_request(
    request: Request, client_kind: ClientKind, *, remember_me: bool
) -> SessionInputDTO:
    """Build session input from validated choices and safe request metadata.

    Args:
        request: The inbound HTTP request.
        client_kind: The validated client platform.
        remember_me: The persistence choice.

    Returns:
        The session input stored by the application layer.
    """
    client_ip = None
    if request.client is not None:
        try:
            client_ip = ip_address(request.client.host)
        except ValueError:
            client_ip = None
    user_agent = request.headers.get("user-agent")
    return SessionInputDTO(
        client_kind=client_kind,
        remember_me=remember_me,
        ip_address=client_ip,
        user_agent=user_agent[:_MAX_USER_AGENT_LENGTH] if user_agent else None,
    )
