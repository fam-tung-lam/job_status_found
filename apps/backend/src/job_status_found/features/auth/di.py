"""Dependency providers that assemble the auth feature."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import partial
from typing import Annotated

from anyio import CapacityLimiter
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
from job_status_found.features.auth.application.use_cases.sign_up_with_password_use_case import (
    SignUpSettings,
    SignUpWithPasswordUseCase,
)
from job_status_found.features.auth.auth_settings import (
    AuthSettings,
    get_auth_settings,
)
from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy
from job_status_found.features.auth.infrastructure.adapters.deferred_auth_email_sender import (
    DeferredAuthEmailSender,
)
from job_status_found.features.auth.infrastructure.adapters.smtp_auth_email_sender import (
    SmtpAuthEmailSender,
)
from job_status_found.features.auth.infrastructure.adapters.sql_auth_event_repository import (
    SqlAuthEventRepository,
)
from job_status_found.features.auth.infrastructure.adapters.sql_email_challenge_repository import (
    SqlEmailChallengeRepository,
)
from job_status_found.features.auth.infrastructure.adapters.sql_password_credential_repository import (  # noqa: E501 - the formatter cannot wrap a module path
    SqlPasswordCredentialRepository,
)
from job_status_found.features.auth.infrastructure.adapters.sql_user_repository import (
    SqlUserRepository,
)
from job_status_found.features.auth.infrastructure.helpers.generate_verification_code import (
    generate_verification_code,
)
from job_status_found.features.auth.infrastructure.helpers.hash_password import hash_password
from job_status_found.features.auth.infrastructure.helpers.hash_verification_code import (
    hash_verification_code,
)
from job_status_found.features.core import (
    SmtpEmailSenderClient,
    UnitOfWork,
    get_database_session,
    get_smtp_email_sender_client,
    get_unit_of_work,
    get_utc_now,
)

_MAX_CONCURRENT_PASSWORD_HASHES = 4
"""Most Argon2id hashes that run at once; four at 64 MiB each fit the 512 MiB container."""


@asynccontextmanager
async def open_auth(app: FastAPI) -> AsyncIterator[None]:
    """Check the auth settings and own the password-hash limiter for the life of the application.

    Invalid or missing auth settings stop the start-up with an error that
    names them. The limiter caps concurrent hashes across all requests, and it
    must be created inside the event loop that serves them.

    Args:
        app: The application whose requests hash passwords.

    Yields:
        Control while the application serves requests.
    """
    get_auth_settings()
    app.state.password_hash_limiter = CapacityLimiter(_MAX_CONCURRENT_PASSWORD_HASHES)
    try:
        yield
    finally:
        del app.state.password_hash_limiter


async def get_hash_password(request: Request) -> Callable[[str], Awaitable[str]]:
    """Provide `hash_password` bound to the application's limiter.

    Args:
        request: The current request, whose application opened the limiter.

    Returns:
        A function that hashes one password under the shared limiter.

    Raises:
        RuntimeError: The application serves requests outside its lifespan.
    """
    password_hash_limiter = getattr(request.app.state, "password_hash_limiter", None)
    if not isinstance(password_hash_limiter, CapacityLimiter):
        error_message = (
            "No password-hash limiter is open; the application's lifespan opens it first."
        )
        raise RuntimeError(error_message)
    return partial(hash_password, limiter=password_hash_limiter)


async def get_sign_up_min_response_time(
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> timedelta:
    """Provide the shortest time an accepted sign-up takes to answer.

    Args:
        settings: The auth settings.

    Returns:
        The configured minimum response time.
    """
    return settings.sign_up_min_response_time


async def get_auth_email_sender(
    background_tasks: BackgroundTasks,
    client: Annotated[SmtpEmailSenderClient, Depends(get_smtp_email_sender_client)],
) -> AuthEmailSender:
    """Provide the sender of auth emails, which delivers after the response.

    Args:
        background_tasks: The current request's background tasks.
        client: The shared SMTP client.

    Returns:
        An SMTP sender deferred to the request's background tasks.
    """
    return DeferredAuthEmailSender(background_tasks, SmtpAuthEmailSender(client))


async def get_sign_up_with_password_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    hash_password: Annotated[Callable[[str], Awaitable[str]], Depends(get_hash_password)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
    email_sender: Annotated[AuthEmailSender, Depends(get_auth_email_sender)],
) -> SignUpWithPasswordUseCase:
    """Provide the email and password sign-up use case.

    Args:
        session: The request's database session.
        settings: The auth settings.
        hash_password: Hashes a password under the application's limiter.
        unit_of_work: Commits the request's session, which the repositories share.
        utc_now: Reads the current time.
        email_sender: The sender of the code or the notice.

    Returns:
        A `SignUpWithPasswordUseCase` on the request's transaction.
    """
    return SignUpWithPasswordUseCase(
        users=SqlUserRepository(session),
        password_credentials=SqlPasswordCredentialRepository(session),
        email_challenges=SqlEmailChallengeRepository(session),
        auth_events=SqlAuthEventRepository(session),
        unit_of_work=unit_of_work,
        hash_password=hash_password,
        generate_verification_code=generate_verification_code,
        hash_verification_code=partial(
            hash_verification_code, hmac_key=settings.hmac_key.get_secret_value().encode()
        ),
        utc_now=utc_now,
        email_sender=email_sender,
        settings=SignUpSettings(
            password_policy=PasswordPolicy(min_length=settings.password_min_length),
            terms_version=settings.terms_version,
            verification_code_lifetime=settings.verification_code_lifetime,
            email_send_interval=settings.verification_code_send_interval,
        ),
    )
