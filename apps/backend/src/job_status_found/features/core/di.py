"""Dependency providers every feature's `di.py` assembles its use cases from."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.core.app_settings import AppSettings, get_settings
from job_status_found.features.core.application.ports.clock import Clock
from job_status_found.features.core.application.ports.unit_of_work import UnitOfWork
from job_status_found.features.core.infrastructure.adapters.sql_unit_of_work import SqlUnitOfWork
from job_status_found.features.core.infrastructure.adapters.system_clock import SystemClock
from job_status_found.features.core.infrastructure.clients.smtp_email_sender_client import (
    SmtpEmailSenderClient,
)
from job_status_found.features.core.infrastructure.db.db import get_database_session


async def get_clock() -> Clock:
    """Provide the clock use cases read the time from.

    Returns:
        The system clock in UTC.
    """
    return SystemClock()


async def get_unit_of_work(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> UnitOfWork:
    """Provide the unit of work that commits the request's database session.

    FastAPI resolves `get_database_session` once per request, so the unit of
    work commits the same session every SQL repository of the request writes
    into.

    Args:
        session: The request's database session.

    Returns:
        A `SqlUnitOfWork` on the request's session.
    """
    return SqlUnitOfWork(session)


async def get_smtp_email_sender_client(
    settings: Annotated[AppSettings, Depends(get_settings)],
) -> SmtpEmailSenderClient:
    """Provide the client that sends every feature's email over SMTP.

    Args:
        settings: The application settings with the SMTP server.

    Returns:
        A client for the configured SMTP server.
    """
    password = settings.smtp_password
    return SmtpEmailSenderClient(
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        security=settings.smtp_security,
        username=settings.smtp_username,
        password=password.get_secret_value() if password is not None else None,
        sender=settings.smtp_sender,
    )
