"""Dependency providers that assemble the auth feature."""

import hmac
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import partial
from typing import Annotated

from anyio import CapacityLimiter
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from job_status_found.features.auth.application.ports.access_token_codec import AccessTokenCodec
from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
from job_status_found.features.auth.application.use_cases.authenticate_access_token_use_case import (  # noqa: E501
    AuthenticateAccessTokenUseCase,
)
from job_status_found.features.auth.application.use_cases.confirm_email_verification_use_case import (  # noqa: E501
    ConfirmEmailVerificationUseCase,
    EmailVerificationSettings,
)
from job_status_found.features.auth.application.use_cases.get_current_user_use_case import (
    GetCurrentUserUseCase,
)
from job_status_found.features.auth.application.use_cases.issue_password_session_use_case import (
    IssuePasswordSessionSettings,
    IssuePasswordSessionUseCase,
)
from job_status_found.features.auth.application.use_cases.issue_rotated_tokens_use_case import (
    IssueRotatedTokensSettings,
    IssueRotatedTokensUseCase,
)
from job_status_found.features.auth.application.use_cases.refresh_session_use_case import (
    RefreshSessionUseCase,
    SessionRefreshSettings,
)
from job_status_found.features.auth.application.use_cases.require_user_role_use_case import (
    RequireUserRoleUseCase,
)
from job_status_found.features.auth.application.use_cases.resend_email_verification_use_case import (  # noqa: E501
    ResendEmailVerificationSettings,
    ResendEmailVerificationUseCase,
)
from job_status_found.features.auth.application.use_cases.sign_in_with_password_use_case import (
    PasswordSignInSettings,
    SignInWithPasswordUseCase,
)
from job_status_found.features.auth.application.use_cases.sign_out_use_case import SignOutUseCase
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
from job_status_found.features.auth.infrastructure.adapters.jwt_access_token_codec import (
    JwtAccessTokenCodec,
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
from job_status_found.features.auth.infrastructure.adapters.sql_session_repository import (
    SqlSessionRepository,
)
from job_status_found.features.auth.infrastructure.adapters.sql_user_repository import (
    SqlUserRepository,
)
from job_status_found.features.auth.infrastructure.helpers.generate_refresh_token import (
    generate_refresh_token,
)
from job_status_found.features.auth.infrastructure.helpers.generate_verification_code import (
    generate_verification_code,
)
from job_status_found.features.auth.infrastructure.helpers.hash_auth_identifier import (
    hash_auth_identifier,
)
from job_status_found.features.auth.infrastructure.helpers.hash_password import hash_password
from job_status_found.features.auth.infrastructure.helpers.hash_refresh_token import (
    hash_refresh_token,
)
from job_status_found.features.auth.infrastructure.helpers.hash_verification_code import (
    hash_verification_code,
)
from job_status_found.features.auth.infrastructure.helpers.verify_and_update_password import (
    verify_and_update_password,
)
from job_status_found.features.auth.presentation.http.v1.refresh_cookie_settings import (
    RefreshCookieSettings,
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
    app.state.dummy_password_hash = await hash_password(
        secrets.token_urlsafe(32), limiter=app.state.password_hash_limiter
    )
    try:
        yield
    finally:
        del app.state.dummy_password_hash
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


async def get_verify_and_update_password(
    request: Request,
) -> Callable[[str, str], Awaitable[tuple[bool, str | None]]]:
    """Provide password verification bound to the application's limiter.

    Args:
        request: The current request, whose application owns the limiter.

    Returns:
        A function that verifies and optionally rehashes one password.

    Raises:
        RuntimeError: The application serves requests outside its lifespan.
    """
    password_hash_limiter = getattr(request.app.state, "password_hash_limiter", None)
    if not isinstance(password_hash_limiter, CapacityLimiter):
        error_message = (
            "No password-hash limiter is open; the application's lifespan opens it first."
        )
        raise RuntimeError(error_message)
    return partial(verify_and_update_password, limiter=password_hash_limiter)


async def get_dummy_password_hash(request: Request) -> str:
    """Provide the process-lifetime dummy Argon2id hash.

    Args:
        request: The current request, whose application owns the dummy hash.

    Returns:
        The hash used to equalize unknown and social-only accounts.

    Raises:
        RuntimeError: The application serves requests outside its lifespan.
    """
    dummy_password_hash = getattr(request.app.state, "dummy_password_hash", None)
    if not isinstance(dummy_password_hash, str):
        error_message = "No dummy password hash exists; the application's lifespan creates it."
        raise RuntimeError(error_message)
    return dummy_password_hash


async def get_access_token_codec(
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> AccessTokenCodec:
    """Provide the configured JWT access-token codec.

    Args:
        settings: The auth settings and key ring.

    Returns:
        The codec that signs with the active key and verifies with every key.
    """
    return JwtAccessTokenCodec(
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        signing_key_id=settings.jwt_signing_key_id,
        key_ring={
            key_id: secret.get_secret_value().encode()
            for key_id, secret in settings.jwt_key_ring.items()
        },
        lifetime=settings.access_token_lifetime,
    )


async def get_issue_password_session_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    access_tokens: Annotated[AccessTokenCodec, Depends(get_access_token_codec)],
) -> IssuePasswordSessionUseCase:
    """Provide initial password-session issuance on the request transaction.

    Args:
        session: The request's database session.
        settings: The configured session lifetimes.
        access_tokens: Issues first-party access tokens.

    Returns:
        The configured initial password-session use case.
    """
    return IssuePasswordSessionUseCase(
        sessions=SqlSessionRepository(session),
        access_tokens=access_tokens,
        generate_refresh_token=generate_refresh_token,
        hash_refresh_token=hash_refresh_token,
        settings=IssuePasswordSessionSettings(
            access_token_lifetime=settings.access_token_lifetime,
            persistent_idle_lifetime=settings.persistent_session_idle_lifetime,
            persistent_absolute_lifetime=settings.persistent_session_absolute_lifetime,
            non_persistent_idle_lifetime=settings.non_persistent_session_idle_lifetime,
            non_persistent_absolute_lifetime=settings.non_persistent_session_absolute_lifetime,
        ),
    )


async def get_issue_rotated_tokens_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    access_tokens: Annotated[AccessTokenCodec, Depends(get_access_token_codec)],
) -> IssueRotatedTokensUseCase:
    """Provide rotated-token issuance on the request transaction.

    Args:
        session: The request's database session.
        settings: The configured access-token lifetime.
        access_tokens: Issues first-party access tokens.

    Returns:
        The configured rotated-token use case.
    """
    return IssueRotatedTokensUseCase(
        sessions=SqlSessionRepository(session),
        access_tokens=access_tokens,
        generate_refresh_token=generate_refresh_token,
        hash_refresh_token=hash_refresh_token,
        settings=IssueRotatedTokensSettings(access_token_lifetime=settings.access_token_lifetime),
    )


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


async def get_refresh_cookie_settings(
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> RefreshCookieSettings:
    """Provide the web refresh-cookie contract.

    Args:
        settings: The auth settings.

    Returns:
        The cookie name, security flag, and persistent maximum age.
    """
    return RefreshCookieSettings(
        name=settings.refresh_cookie_name,
        secure=settings.cookie_secure,
        persistent_max_age=settings.persistent_session_idle_lifetime,
    )


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
            verification_code_lifetime=settings.verification_code_lifetime,
            email_send_interval=settings.verification_code_send_interval,
        ),
    )


async def get_confirm_email_verification_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    verify_password: Annotated[
        Callable[[str, str], Awaitable[tuple[bool, str | None]]],
        Depends(get_verify_and_update_password),
    ],
    dummy_password_hash: Annotated[str, Depends(get_dummy_password_hash)],
    issue_password_session: Annotated[
        IssuePasswordSessionUseCase, Depends(get_issue_password_session_use_case)
    ],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
) -> ConfirmEmailVerificationUseCase:
    """Provide email confirmation on the request transaction.

    Args:
        session: The request's database session.
        settings: The auth settings.
        verify_password: Performs the password half of the joint proof.
        dummy_password_hash: Equalizes unknown addresses.
        issue_password_session: Opens the successful password session.
        unit_of_work: Commits the request transaction.
        utc_now: Reads the current time.

    Returns:
        The configured confirmation use case.
    """
    return ConfirmEmailVerificationUseCase(
        users=SqlUserRepository(session),
        password_credentials=SqlPasswordCredentialRepository(session),
        email_challenges=SqlEmailChallengeRepository(session),
        auth_events=SqlAuthEventRepository(session),
        issue_password_session=issue_password_session,
        unit_of_work=unit_of_work,
        verify_and_update_password=verify_password,
        hash_verification_code=partial(
            hash_verification_code, hmac_key=settings.hmac_key.get_secret_value().encode()
        ),
        are_hashes_equal=hmac.compare_digest,
        utc_now=utc_now,
        dummy_password_hash=dummy_password_hash,
        settings=EmailVerificationSettings(code_lifetime=settings.verification_code_lifetime),
    )


async def get_resend_email_verification_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
    email_sender: Annotated[AuthEmailSender, Depends(get_auth_email_sender)],
) -> ResendEmailVerificationUseCase:
    """Provide verification-code resend on the request transaction.

    Args:
        session: The request's database session.
        settings: The auth settings.
        unit_of_work: Commits before queued mail.
        utc_now: Reads the current time.
        email_sender: Queues a replacement code.

    Returns:
        The configured resend use case.
    """
    return ResendEmailVerificationUseCase(
        users=SqlUserRepository(session),
        email_challenges=SqlEmailChallengeRepository(session),
        unit_of_work=unit_of_work,
        generate_verification_code=generate_verification_code,
        hash_verification_code=partial(
            hash_verification_code, hmac_key=settings.hmac_key.get_secret_value().encode()
        ),
        utc_now=utc_now,
        email_sender=email_sender,
        settings=ResendEmailVerificationSettings(
            code_lifetime=settings.verification_code_lifetime,
            send_interval=settings.verification_code_send_interval,
        ),
    )


async def get_sign_in_with_password_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    verify_password: Annotated[
        Callable[[str, str], Awaitable[tuple[bool, str | None]]],
        Depends(get_verify_and_update_password),
    ],
    dummy_password_hash: Annotated[str, Depends(get_dummy_password_hash)],
    issue_password_session: Annotated[
        IssuePasswordSessionUseCase, Depends(get_issue_password_session_use_case)
    ],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
    email_sender: Annotated[AuthEmailSender, Depends(get_auth_email_sender)],
) -> SignInWithPasswordUseCase:
    """Provide password sign-in on the request transaction.

    Args:
        session: The request's database session.
        settings: The auth settings.
        verify_password: Performs real and dummy Argon2id checks.
        dummy_password_hash: Equalizes unknown and social-only accounts.
        issue_password_session: Opens a successful password session.
        unit_of_work: Commits every persisted outcome.
        utc_now: Reads the current time.
        email_sender: Queues an unverified account's replacement code.

    Returns:
        The configured password sign-in use case.
    """
    hmac_key = settings.hmac_key.get_secret_value().encode()
    return SignInWithPasswordUseCase(
        users=SqlUserRepository(session),
        password_credentials=SqlPasswordCredentialRepository(session),
        email_challenges=SqlEmailChallengeRepository(session),
        auth_events=SqlAuthEventRepository(session),
        issue_password_session=issue_password_session,
        unit_of_work=unit_of_work,
        verify_and_update_password=verify_password,
        hash_auth_identifier=partial(hash_auth_identifier, hmac_key=hmac_key),
        generate_verification_code=generate_verification_code,
        hash_verification_code=partial(hash_verification_code, hmac_key=hmac_key),
        utc_now=utc_now,
        email_sender=email_sender,
        dummy_password_hash=dummy_password_hash,
        settings=PasswordSignInSettings(
            verification_code_lifetime=settings.verification_code_lifetime,
            verification_code_send_interval=settings.verification_code_send_interval,
        ),
    )


async def get_authenticate_access_token_use_case(
    access_tokens: Annotated[AccessTokenCodec, Depends(get_access_token_codec)],
) -> AuthenticateAccessTokenUseCase:
    """Provide stateless access-token authentication.

    Args:
        access_tokens: The configured JWT codec.

    Returns:
        The authentication use case.
    """
    return AuthenticateAccessTokenUseCase(access_tokens=access_tokens)


async def get_current_user_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GetCurrentUserUseCase:
    """Provide current-user lookup on the request session.

    Args:
        session: The request's database session.

    Returns:
        The current-user use case.
    """
    return GetCurrentUserUseCase(users=SqlUserRepository(session))


async def get_require_user_role_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> RequireUserRoleUseCase:
    """Provide stored-role authorization on the request session.

    Args:
        session: The request's database session.

    Returns:
        The stored-role use case.
    """
    return RequireUserRoleUseCase(users=SqlUserRepository(session))


async def get_refresh_session_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    issue_rotated_tokens: Annotated[
        IssueRotatedTokensUseCase, Depends(get_issue_rotated_tokens_use_case)
    ],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
) -> RefreshSessionUseCase:
    """Provide refresh rotation on the request transaction.

    Args:
        session: The request's database session.
        settings: The refresh grace and session lifetimes.
        issue_rotated_tokens: Issues replacement credentials.
        unit_of_work: Commits each refresh outcome.
        utc_now: Reads the current time.

    Returns:
        The configured refresh use case.
    """
    return RefreshSessionUseCase(
        sessions=SqlSessionRepository(session),
        auth_events=SqlAuthEventRepository(session),
        issue_rotated_tokens=issue_rotated_tokens,
        unit_of_work=unit_of_work,
        hash_refresh_token=hash_refresh_token,
        utc_now=utc_now,
        settings=SessionRefreshSettings(
            persistent_idle_lifetime=settings.persistent_session_idle_lifetime,
            non_persistent_idle_lifetime=settings.non_persistent_session_idle_lifetime,
            reuse_grace=settings.refresh_reuse_grace,
        ),
    )


async def get_sign_out_use_case(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    utc_now: Annotated[Callable[[], datetime], Depends(get_utc_now)],
) -> SignOutUseCase:
    """Provide idempotent sign-out on the request transaction.

    Args:
        session: The request's database session.
        unit_of_work: Commits the revocation.
        utc_now: Reads the current time.

    Returns:
        The sign-out use case.
    """
    return SignOutUseCase(
        sessions=SqlSessionRepository(session),
        unit_of_work=unit_of_work,
        hash_refresh_token=hash_refresh_token,
        utc_now=utc_now,
    )
