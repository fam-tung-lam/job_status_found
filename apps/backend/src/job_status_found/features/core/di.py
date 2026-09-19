"""Dependency providers every feature's `di.py` assembles its use cases from."""

from collections.abc import Callable
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.core.app_settings import AppSettings, get_app_settings
from job_status_found.features.core.application.ports.unit_of_work import UnitOfWork
from job_status_found.features.core.infrastructure.adapters.sql_unit_of_work import SqlUnitOfWork
from job_status_found.features.core.infrastructure.clients.smtp_email_sender_client import (
    SmtpEmailSenderClient,
)
from job_status_found.features.core.infrastructure.db.db import get_database_session
from job_status_found.features.core.infrastructure.helpers.utc_now import utc_now


async def get_utc_now() -> Callable[[], datetime]:
    """Provide the function use cases read the current time from.

    A provider, rather than a direct import in each `di.py`, so an API test can
    override it and control the time.

    Returns:
        `utc_now`, which reads the system clock in UTC.
    """
    return utc_now


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
    settings: Annotated[AppSettings, Depends(get_app_settings)],
) -> SmtpEmailSenderClient:
    """Provide the client that sends every feature's email over SMTP.

    Args:
        settings: The application settings with the SMTP server.

    Returns:
        A client for the configured SMTP server.
    """
    smtp_password = settings.smtp_password
    return SmtpEmailSenderClient(
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        security=settings.smtp_security,
        username=settings.smtp_username,
        password=smtp_password.get_secret_value() if smtp_password is not None else None,
        from_address=settings.smtp_sender,
    )
