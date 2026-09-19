"""Sign in a verified account with its password."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_auth_event_dto import NewAuthEventDTO
from job_status_found.features.auth.application.dtos.new_email_challenge_dto import (
    NewEmailChallengeDTO,
)
from job_status_found.features.auth.application.dtos.password_sign_in_input_dto import (
    PasswordSignInInputDTO,
)
from job_status_found.features.auth.application.dtos.token_pair_dto import TokenPairDTO
from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
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
from job_status_found.features.auth.domain.failures.password_sign_in_failure import (
    PasswordSignInAccountUnavailableFailure,
    PasswordSignInEmailNotVerifiedFailure,
    PasswordSignInInvalidCredentialsFailure,
)
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.core import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PasswordSignInSettings:
    """The verification-code rules used by unverified password accounts."""

    verification_code_lifetime: timedelta
    """How long a newly sent verification code works."""

    verification_code_send_interval: timedelta
    """Shortest interval between code emails."""


class SignInWithPasswordUseCase:
    """Verify a password, enforce account state, and open a session."""

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
        hash_auth_identifier: Callable[[str], bytes],
        generate_verification_code: Callable[[], str],
        hash_verification_code: Callable[[str], bytes],
        utc_now: Callable[[], datetime],
        email_sender: AuthEmailSender,
        dummy_password_hash: str,
        settings: PasswordSignInSettings,
    ) -> None:
        """Keep every collaborator and rule of password sign-in.

        Args:
            users: Finds and locks accounts by normalized email.
            password_credentials: Reads and strengthens password hashes.
            email_challenges: Paces and replaces verification codes.
            auth_events: Records every failed password check.
            issue_password_session: Opens a successful password session.
            unit_of_work: Commits the operation's writes together.
            verify_and_update_password: Performs one real or dummy Argon2id check.
            hash_auth_identifier: Hides the normalized email in audit rows.
            generate_verification_code: Creates a code for an unverified account.
            hash_verification_code: Hashes that code for storage.
            utc_now: Tells the current instant.
            email_sender: Queues the code only after commit.
            dummy_password_hash: Equalizes unknown and social-only accounts.
            settings: The code lifetime and send interval.
        """
        self._users = users
        self._password_credentials = password_credentials
        self._email_challenges = email_challenges
        self._auth_events = auth_events
        self._issue_password_session = issue_password_session
        self._unit_of_work = unit_of_work
        self._verify_and_update_password = verify_and_update_password
        self._hash_auth_identifier = hash_auth_identifier
        self._generate_verification_code = generate_verification_code
        self._hash_verification_code = hash_verification_code
        self._utc_now = utc_now
        self._email_sender = email_sender
        self._dummy_password_hash = dummy_password_hash
        self._settings = settings

    async def invoke(self, sign_in: PasswordSignInInputDTO) -> TokenPairDTO:
        """Sign in with a password and return a committed session's credentials.

        Args:
            sign_in: The credentials and session choices.

        Returns:
            The new session's credentials.

        Raises:
            PasswordSignInInvalidCredentialsFailure: The password account is not proved.
            PasswordSignInEmailNotVerifiedFailure: The password is right but the
                email is unverified.
            PasswordSignInAccountUnavailableFailure: The password is right but the
                account is blocked.
        """
        now = self._utc_now()
        normalized_email = EmailAddress(sign_in.email).normalized
        user = await self._users.lock_user_by_normalized_email(normalized_email)
        password_hash = (
            await self._password_credentials.find_password_hash(user.id)
            if user is not None
            else None
        )

        # Every branch performs exactly one Argon2id verification.
        is_password_valid, replacement_hash = await self._verify_and_update_password(
            sign_in.password, password_hash or self._dummy_password_hash
        )
        if user is None or password_hash is None or not is_password_valid:
            identifier_hash = self._hash_auth_identifier(normalized_email)
            await self._auth_events.create_auth_event(
                NewAuthEventDTO(
                    owner_id=user.id if user is not None else None,
                    event_type=AuthEventType.SIGN_IN_FAILED,
                    identifier_hash=identifier_hash,
                    ip_address=sign_in.session.ip_address,
                    user_agent=sign_in.session.user_agent,
                    occurred_at=now,
                )
            )
            await self._unit_of_work.commit()
            logger.warning(
                "Password sign-in failed; account known: %s; identifier hash: %s",
                user is not None,
                identifier_hash.hex(),
            )
            raise PasswordSignInInvalidCredentialsFailure

        # A proved but unverified account gets a paced replacement code.
        if not user.is_email_verified:
            verification_code = await self._replace_verification_code_if_interval_passed(
                user.id, now
            )
            await self._unit_of_work.commit()
            if verification_code is not None:
                await self._email_sender.send_verification_code(
                    user.email, verification_code, self._settings.verification_code_lifetime
                )
            raise PasswordSignInEmailNotVerifiedFailure

        # Account state is disclosed only after the password is proved.
        if not user.is_available:
            await self._unit_of_work.commit()
            raise PasswordSignInAccountUnavailableFailure

        # Strengthen old parameters and open the session in one commit.
        if replacement_hash is not None:
            await self._password_credentials.set_password_hash(user.id, replacement_hash, now)
        token_pair = await self._issue_password_session.invoke(
            user.id, user.role, sign_in.session, now
        )
        await self._unit_of_work.commit()
        return token_pair

    async def _replace_verification_code_if_interval_passed(
        self, owner_id: UUID, now: datetime
    ) -> str | None:
        """Replace an unverified account's code when its send interval passed.

        Args:
            owner_id: The unverified account id.
            now: The sign-in instant.

        Returns:
            The new clear code to mail, or `None` when sending is suppressed.
        """
        last_sent_at = await self._email_challenges.find_last_email_challenge_sent_at(
            owner_id, EmailChallengePurpose.VERIFY_EMAIL
        )
        if (
            last_sent_at is not None
            and now - last_sent_at < self._settings.verification_code_send_interval
        ):
            return None
        code = self._generate_verification_code()
        await self._email_challenges.replace_open_email_challenge(
            NewEmailChallengeDTO(
                owner_id=owner_id,
                purpose=EmailChallengePurpose.VERIFY_EMAIL,
                secret_hash=self._hash_verification_code(code),
                created_at=now,
                expires_at=now + self._settings.verification_code_lifetime,
            )
        )
        return code
