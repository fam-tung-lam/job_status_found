"""Confirm a mailbox and its matching password, then open a session."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from job_status_found.features.auth.application.dtos.confirm_email_verification_input_dto import (
    ConfirmEmailVerificationInputDTO,
)
from job_status_found.features.auth.application.dtos.new_auth_event_dto import NewAuthEventDTO
from job_status_found.features.auth.application.dtos.token_pair_dto import TokenPairDTO
from job_status_found.features.auth.application.ports.auth_event_repository import (
    AuthEventRepository,
)
from job_status_found.features.auth.application.ports.email_challenge_repository import (
    EmailChallengeRepository,
)
from job_status_found.features.auth.application.ports.password_credential_repository import (
    PasswordCredentialRepository,
)
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.application.use_cases.issue_password_session_use_case import (
    IssuePasswordSessionUseCase,
)
from job_status_found.features.auth.domain.failures.email_verification_failure import (
    EmailVerificationCodeInvalidFailure,
)
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.core import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EmailVerificationSettings:
    """The expiry window and cumulative failed-proof cap."""

    code_lifetime: timedelta
    """The rolling window over which failures survive challenge replacement."""

    max_failed_attempts: int = 5
    """Most failed code-password pairs allowed in the rolling window."""


class ConfirmEmailVerificationUseCase:
    """Verify one code-password pair and atomically open its first session."""

    def __init__(
        self,
        *,
        users: UserRepository,
        password_credentials: PasswordCredentialRepository,
        email_challenges: EmailChallengeRepository,
        auth_events: AuthEventRepository,
        issue_password_session: IssuePasswordSessionUseCase,
        unit_of_work: UnitOfWork,
        verify_and_update_password: Callable[[str, str], Awaitable[tuple[bool, str | None]]],
        hash_verification_code: Callable[[str], bytes],
        are_hashes_equal: Callable[[bytes, bytes], bool],
        utc_now: Callable[[], datetime],
        dummy_password_hash: str,
        settings: EmailVerificationSettings,
    ) -> None:
        """Keep every collaborator used by email verification.

        Args:
            users: Reads and verifies accounts.
            password_credentials: Reads and optionally strengthens password hashes.
            email_challenges: Locks and consumes emailed codes.
            auth_events: Carries failed attempts across replaced challenges.
            issue_password_session: Creates the first session and credentials.
            unit_of_work: Commits all writes together.
            verify_and_update_password: Verifies Argon2id off the event loop.
            hash_verification_code: Computes the submitted code's keyed hash.
            are_hashes_equal: Compares fixed-size digests without timing leakage.
            utc_now: Tells the current instant.
            dummy_password_hash: Equalizes an unknown mailbox with a real password check.
            settings: The failure window and cap.
        """
        self._users = users
        self._password_credentials = password_credentials
        self._email_challenges = email_challenges
        self._auth_events = auth_events
        self._issue_password_session = issue_password_session
        self._unit_of_work = unit_of_work
        self._verify_and_update_password = verify_and_update_password
        self._hash_verification_code = hash_verification_code
        self._are_hashes_equal = are_hashes_equal
        self._utc_now = utc_now
        self._dummy_password_hash = dummy_password_hash
        self._settings = settings

    async def invoke(self, confirmation: ConfirmEmailVerificationInputDTO) -> TokenPairDTO:
        """Confirm a code-password pair and return a committed session's credentials.

        Args:
            confirmation: The submitted proof and session choices.

        Returns:
            The new session's credentials.

        Raises:
            EmailVerificationCodeInvalidFailure: Any part of the proof is unusable.
            AssertionError: An internal invariant loses a proved account or challenge.
        """
        # Lock a known account and always pay for one Argon2id verification.
        now = self._utc_now()
        normalized_email = EmailAddress(confirmation.email).normalized
        user = await self._users.lock_user_by_normalized_email(normalized_email)
        password_hash = (
            await self._password_credentials.find_password_hash(user.id)
            if user is not None
            else None
        )
        is_password_valid, replacement_hash = await self._verify_and_update_password(
            confirmation.password, password_hash or self._dummy_password_hash
        )

        # Read the open challenge and the rolling failures only for an unverified account.
        challenge = None
        recent_failure_count = 0
        if user is not None and not user.is_email_verified:
            challenge = await self._email_challenges.lock_open_email_challenge(
                user.id, EmailChallengePurpose.VERIFY_EMAIL
            )
            recent_failure_count = await self._auth_events.count_auth_events_since(
                user.id,
                AuthEventType.EMAIL_VERIFICATION_FAILED,
                now - self._settings.code_lifetime,
            )

        submitted_hash = self._hash_verification_code(confirmation.code)
        is_challenge_valid = (
            challenge is not None
            and challenge.expires_at > now
            and challenge.attempt_count < self._settings.max_failed_attempts
            and recent_failure_count < self._settings.max_failed_attempts
            and self._are_hashes_equal(challenge.secret_hash, submitted_hash)
        )

        # Persist every failed pair before returning the same generic failure.
        if (
            user is None
            or user.is_email_verified
            or not is_password_valid
            or not is_challenge_valid
        ):
            if user is not None and not user.is_email_verified:
                next_failure_count = recent_failure_count + 1
                await self._auth_events.create_auth_event(
                    NewAuthEventDTO(
                        owner_id=user.id,
                        event_type=AuthEventType.EMAIL_VERIFICATION_FAILED,
                        occurred_at=now,
                    )
                )
                if challenge is not None:
                    next_challenge_attempt_count = challenge.attempt_count + 1
                    is_exhausted = (
                        next_challenge_attempt_count >= self._settings.max_failed_attempts
                        or next_failure_count >= self._settings.max_failed_attempts
                    )
                    await self._email_challenges.register_wrong_email_challenge_answer(
                        challenge.id,
                        attempt_count=next_challenge_attempt_count,
                        consumed_at=now if is_exhausted else None,
                    )
            await self._unit_of_work.commit()
            if user is not None and not user.is_email_verified:
                logger.warning("Email verification failed for user %s", user.id)
            raise EmailVerificationCodeInvalidFailure

        # Consume the jointly proved challenge, strengthen the password if needed,
        # and open the session in one transaction.
        if challenge is None or user is None:
            raise AssertionError("A valid verification proof must have an account and challenge.")
        await self._email_challenges.consume_email_challenge(challenge.id, now)
        await self._users.set_email_verified_at(user.id, now)
        if replacement_hash is not None:
            await self._password_credentials.set_password_hash(user.id, replacement_hash, now)
        token_pair = await self._issue_password_session.invoke(
            user.id, user.role, confirmation.session, now
        )
        await self._unit_of_work.commit()
        return token_pair
