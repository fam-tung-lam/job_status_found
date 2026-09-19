"""Dependency providers that assemble the auth feature."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from anyio import CapacityLimiter
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
from job_status_found.features.auth.application.ports.password_hasher import PasswordHasher
from job_status_found.features.auth.application.use_cases.sign_up_with_password_use_case import (
    SignUpSettings,
    SignUpWithPasswordUseCase,
)
from job_status_found.features.auth.auth_settings import (
    AuthSettings,
    get_auth_settings,
)
from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy
from job_status_found.features.auth.infrastructure.adapters.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from job_status_found.features.auth.infrastructure.adapters.deferred_auth_email_sender import (
    DeferredAuthEmailSender,
)
from job_status_found.features.auth.infrastructure.adapters.hmac_verification_code_hasher import (
    HmacVerificationCodeHasher,
)
from job_status_found.features.auth.infrastructure.adapters.secure_random_verification_code_generator import (  # noqa: E501 - the formatter cannot wrap a module path
    SecureRandomVerificationCodeGenerator,
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
from job_status_found.features.core import (
    Clock,
    SmtpEmailSenderClient,
    UnitOfWork,
    get_clock,
    get_database_session,
    get_smtp_email_sender_client,
    get_unit_of_work,
)

_CONCURRENT_PASSWORD_HASHES = 4
"""Most Argon2id hashes that run at once; four at 64 MiB each fit the 512 MiB container."""


@asynccontextmanager
async def open_auth(app: FastAPI) -> AsyncIterator[None]:
    """Check the auth settings and own the password hasher for the life of the application.

    Invalid or missing auth settings stop the start-up with an error that
    names them. The hasher's limiter caps concurrent hashes across all
    requests, and it must be created inside the event loop that serves them.

    Args:
        app: The application whose requests hash passwords.

    Yields:
        Control while the application serves requests.
    """
    get_auth_settings()
    app.state.password_hasher = Argon2PasswordHasher(CapacityLimiter(_CONCURRENT_PASSWORD_HASHES))
    try:
        yield
    finally:
        del app.state.password_hasher


async def get_password_hasher(request: Request) -> PasswordHasher:
    """Provide the application's password hasher.

    Args:
        request: The current request, whose application opened the hasher.

    Returns:
        The hasher `open_auth` created.

    Raises:
        RuntimeError: The application serves requests outside its lifespan.
    """
    password_hasher = getattr(request.app.state, "password_hasher", None)
    if not isinstance(password_hasher, Argon2PasswordHasher):
        msg = "No password hasher is open; the application's lifespan opens it before requests."
        raise RuntimeError(msg)
    return password_hasher


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
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    clock: Annotated[Clock, Depends(get_clock)],
    email_sender: Annotated[AuthEmailSender, Depends(get_auth_email_sender)],
) -> SignUpWithPasswordUseCase:
    """Provide the email and password sign-up use case.

    Args:
        session: The request's database session.
        settings: The auth settings.
        password_hasher: The application's password hasher.
        unit_of_work: Commits the request's session, which the repositories share.
        clock: The clock to read the time from.
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
        password_hasher=password_hasher,
        verification_code_generator=SecureRandomVerificationCodeGenerator(),
        verification_code_hasher=HmacVerificationCodeHasher(
            settings.hmac_key.get_secret_value().encode()
        ),
        clock=clock,
        email_sender=email_sender,
        settings=SignUpSettings(
            password_policy=PasswordPolicy(min_length=settings.password_min_length),
            terms_version=settings.terms_version,
            verification_code_lifetime=settings.verification_code_lifetime,
            email_send_interval=settings.verification_code_send_interval,
        ),
    )
