"""Resend a verification code without revealing whether an account exists."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from job_status_found.features.auth.application.dtos.new_email_challenge_dto import (
    NewEmailChallengeDTO,
)
from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
from job_status_found.features.auth.application.ports.email_challenge_repository import (
    EmailChallengeRepository,
)
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.core import UnitOfWork


@dataclass(frozen=True, slots=True)
class ResendEmailVerificationSettings:
    """The configured verification-code lifetime and send interval."""

    code_lifetime: timedelta
    """How long the replacement code works."""

    send_interval: timedelta
    """Shortest interval between code emails to one account."""


class ResendEmailVerificationUseCase:
    """Replace and mail an unverified account's code at most once per interval."""

    def __init__(
        self,
        *,
        users: UserRepository,
        email_challenges: EmailChallengeRepository,
        unit_of_work: UnitOfWork,
        generate_verification_code: Callable[[], str],
        hash_verification_code: Callable[[str], bytes],
        utc_now: Callable[[], datetime],
        email_sender: AuthEmailSender,
        settings: ResendEmailVerificationSettings,
    ) -> None:
        """Keep the storage, helpers, clock, sender, and rules.

        Args:
            users: Locks a known account while the send decision is made.
            email_challenges: Reads and replaces verification challenges.
            unit_of_work: Commits before any email is queued.
            generate_verification_code: Creates a six-digit code.
            hash_verification_code: Computes its stored keyed hash.
            utc_now: Tells the current instant.
            email_sender: Queues the code after commit.
            settings: The lifetime and send interval.
        """
        self._users = users
        self._email_challenges = email_challenges
        self._unit_of_work = unit_of_work
        self._generate_verification_code = generate_verification_code
        self._hash_verification_code = hash_verification_code
        self._utc_now = utc_now
        self._email_sender = email_sender
        self._settings = settings

    async def invoke(self, email: str) -> None:
        """Queue a replacement code when allowed, with no observable branch result.

        Args:
            email: The syntactically validated mailbox.
        """
        now = self._utc_now()
        user = await self._users.lock_user_by_normalized_email(EmailAddress(email).normalized)
        verification_code: str | None = None

        # Only an unverified account outside the interval receives a replacement.
        if user is not None and not user.is_email_verified:
            last_sent_at = await self._email_challenges.find_last_email_challenge_sent_at(
                user.id, EmailChallengePurpose.VERIFY_EMAIL
            )
            can_send = last_sent_at is None or now - last_sent_at >= self._settings.send_interval
            if can_send:
                verification_code = self._generate_verification_code()
                await self._email_challenges.replace_open_email_challenge(
                    NewEmailChallengeDTO(
                        owner_id=user.id,
                        purpose=EmailChallengePurpose.VERIFY_EMAIL,
                        secret_hash=self._hash_verification_code(verification_code),
                        created_at=now,
                        expires_at=now + self._settings.code_lifetime,
                    )
                )
        await self._unit_of_work.commit()

        # Queue mail only after the replacement is durable.
        if user is not None and verification_code is not None:
            await self._email_sender.send_verification_code(
                user.email, verification_code, self._settings.code_lifetime
            )
