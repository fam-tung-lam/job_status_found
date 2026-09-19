"""Create an account with email and password, or email its owner instead."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_email_challenge_dto import (
    NewEmailChallengeDTO,
)
from job_status_found.features.auth.application.dtos.sign_up_input_dto import SignUpInputDTO
from job_status_found.features.auth.application.dtos.user_registration_dto import (
    UserRegistrationDTO,
)
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
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.failures.sign_up_failure import (
    SignUpPasswordTooWeakFailure,
)
from job_status_found.features.auth.domain.value_objects.auth_event_type import AuthEventType
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy
from job_status_found.features.core import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SignUpSettings:
    """The configured rules a sign-up applies."""

    password_policy: PasswordPolicy
    """The length bounds a new password must meet."""

    verification_code_lifetime: timedelta
    """How long an emailed verification code stays valid."""

    email_send_interval: timedelta
    """Shortest time between two sign-up emails, a code or a notice, to the same user."""


class SignUpWithPasswordUseCase:
    """Create an unverified account, or email the owner of an existing one.

    The outcome never reveals whether the email already had an account. Every
    branch hashes the password, returns the same result, and emails at most
    once, after the commit:

    - A new email gets an unverified account and a verification code.
    - The email of a verified account changes no account data; its owner gets
      a notice, at most once per send interval.
    - The email of an unverified account takes the new password and name,
      because nobody has proven that mailbox yet, together with a new code that
      replaces the open one. Within the send interval of the last code nothing
      changes: a password replaced without a new email could be confirmed by
      the mailbox owner with the code they already hold.
    """

    def __init__(
        self,
        *,
        users: UserRepository,
        password_credentials: PasswordCredentialRepository,
        email_challenges: EmailChallengeRepository,
        auth_events: AuthEventRepository,
        unit_of_work: UnitOfWork,
        hash_password: Callable[[str], Awaitable[str]],
        generate_verification_code: Callable[[], str],
        hash_verification_code: Callable[[str], bytes],
        utc_now: Callable[[], datetime],
        email_sender: AuthEmailSender,
        settings: SignUpSettings,
    ) -> None:
        """Keep the collaborators and rules of every sign-up.

        Args:
            users: Stores accounts.
            password_credentials: Stores password hashes.
            email_challenges: Stores emailed codes.
            auth_events: Records sent notices, which pace the next one.
            unit_of_work: Commits the writes of every repository at once.
            hash_password: Hashes a password with Argon2id without blocking the
                event loop.
            generate_verification_code: Creates a 6-digit verification code.
            hash_verification_code: Hashes a verification code with the server key.
            utc_now: Tells the current instant.
            email_sender: Delivers the code or the notice.
            settings: The configured rules.
        """
        self._users = users
        self._password_credentials = password_credentials
        self._email_challenges = email_challenges
        self._auth_events = auth_events
        self._unit_of_work = unit_of_work
        self._hash_password = hash_password
        self._generate_verification_code = generate_verification_code
        self._hash_verification_code = hash_verification_code
        self._utc_now = utc_now
        self._email_sender = email_sender
        self._settings = settings

    async def invoke(self, sign_up: SignUpInputDTO) -> None:
        """Sign a person up, committing once and emailing after the commit.

        Args:
            sign_up: What the person submitted.

        Raises:
            SignUpPasswordTooWeakFailure: The password's length is outside the policy.
            RuntimeError: The account holding the email was deleted while this
                sign-up ran.
        """
        # Refuse a password outside the policy before any work or write.
        password_policy = self._settings.password_policy
        if not password_policy.is_length_allowed(sign_up.password):
            raise SignUpPasswordTooWeakFailure(
                min_length=password_policy.min_length, max_length=password_policy.max_length
            )

        # Hash the password in every branch, so no branch answers measurably faster.
        password_hash = await self._hash_password(sign_up.password)
        now = self._utc_now()
        registration = UserRegistrationDTO(
            email=EmailAddress(sign_up.email),
            first_name=sign_up.first_name,
            last_name=sign_up.last_name,
            registered_at=now,
        )

        # A new email gets an account, its password, and its first code.
        new_user = await self._users.create_unverified_user_unless_email_taken(registration)
        if new_user is not None:
            await self._set_password_and_email_first_verification_code(new_user, password_hash, now)
            return

        # The email is taken: lock its account, so a concurrent sign-up waits.
        existing_user = await self._users.lock_user_by_normalized_email(
            registration.email.normalized
        )
        if existing_user is None:
            error_message = (
                "The account holding the signed-up email was deleted during the sign-up."
            )
            raise RuntimeError(error_message)

        # A verified owner gets a notice; an unverified account restarts its sign-up.
        if existing_user.is_email_verified:
            await self._email_existing_account_notice_unless_sent_recently(existing_user, now)
        else:
            await self._restart_unverified_sign_up_unless_code_sent_recently(
                existing_user, registration, password_hash, now
            )

    async def _set_password_and_email_first_verification_code(
        self, user: User, password_hash: str, now: datetime
    ) -> None:
        """Give a just-created account its password and first code, commit, then mail the code.

        Args:
            user: The account `create_unverified_user_unless_email_taken` just created.
            password_hash: The Argon2id hash of the submitted password.
            now: The instant of this sign-up.
        """
        # Store the password and the first code in the account's transaction.
        await self._password_credentials.set_password_hash(user.id, password_hash, now)
        verification_code = await self._issue_verification_code(user.id, now)
        await self._unit_of_work.commit()
        logger.info("Sign-up created unverified user %s", user.id)

        # Mail the code only after the commit, so it never names a discarded code.
        await self._send_verification_code(user, verification_code)

    async def _email_existing_account_notice_unless_sent_recently(
        self, user: User, now: datetime
    ) -> None:
        """Leave a verified account unchanged; mail its owner a notice at most once per interval.

        Args:
            user: The verified account that owns the submitted email.
            now: The instant of this sign-up.
        """
        # Send a notice only when the last one is at least one interval old.
        last_notice_sent_at = await self._auth_events.find_last_auth_event_occurred_at(
            user.id, AuthEventType.EXISTING_ACCOUNT_NOTICE_SENT
        )
        should_send_notice = self._has_send_interval_passed_since(last_notice_sent_at, now)

        # Record the notice, which paces the next one. The commit also ends the
        # transaction that locked the row when nothing was written.
        if should_send_notice:
            await self._auth_events.record_auth_event(
                user.id, AuthEventType.EXISTING_ACCOUNT_NOTICE_SENT, now
            )
        await self._unit_of_work.commit()
        logger.info(
            "Sign-up matched verified user %s; notice sent: %s", user.id, should_send_notice
        )

        # Mail the notice after the commit.
        if should_send_notice:
            await self._email_sender.send_existing_account_notice(user.email)

    async def _restart_unverified_sign_up_unless_code_sent_recently(
        self, user: User, registration: UserRegistrationDTO, password_hash: str, now: datetime
    ) -> None:
        """Replace an unverified account's details and code, unless a code went out too recently.

        Within the send interval nothing changes, so the owner's open code can
        only confirm the password it was mailed for.

        Args:
            user: The unverified account that owns the submitted email.
            registration: The details of this sign-up.
            password_hash: The Argon2id hash of the submitted password.
            now: The instant of this sign-up.
        """
        # Within the send interval of the last code, change nothing. The commit
        # ends the transaction that locked the row.
        last_code_sent_at = await self._email_challenges.find_last_email_challenge_sent_at(
            user.id, EmailChallengePurpose.VERIFY_EMAIL
        )
        if not self._has_send_interval_passed_since(last_code_sent_at, now):
            await self._unit_of_work.commit()
            logger.info("Sign-up left unverified user %s unchanged within the interval", user.id)
            return

        # Replace the name, the password, and the open code in one transaction.
        await self._users.replace_first_and_last_name(user.id, registration)
        await self._password_credentials.set_password_hash(user.id, password_hash, now)
        verification_code = await self._issue_verification_code(user.id, now)
        await self._unit_of_work.commit()
        logger.info("Sign-up replaced the password and code of unverified user %s", user.id)

        # Mail the new code after the commit.
        await self._send_verification_code(user, verification_code)

    def _has_send_interval_passed_since(self, last_sent_at: datetime | None, now: datetime) -> bool:
        """Tell whether another sign-up email may go out to the same user.

        Args:
            last_sent_at: When the last code or notice was sent; `None` if never.
            now: The instant of this sign-up.

        Returns:
            Whether a full send interval has passed, counting its end as passed.
        """
        return last_sent_at is None or now >= last_sent_at + self._settings.email_send_interval

    async def _issue_verification_code(self, user_id: UUID, now: datetime) -> str:
        """Create a code and store its keyed hash, replacing the user's open code.

        Args:
            user_id: The user the code is for.
            now: The instant the code is issued; it expires one lifetime later.

        Returns:
            The code in the clear, to mail after the commit.
        """
        code = self._generate_verification_code()

        await self._email_challenges.replace_open_email_challenge(
            NewEmailChallengeDTO(
                owner_id=user_id,
                purpose=EmailChallengePurpose.VERIFY_EMAIL,
                secret_hash=self._hash_verification_code(code),
                created_at=now,
                expires_at=now + self._settings.verification_code_lifetime,
            )
        )
        return code

    async def _send_verification_code(self, user: User, code: str) -> None:
        """Mail a code to the account's address, stating how long it works.

        Args:
            user: The account to mail.
            code: The code in the clear.
        """
        await self._email_sender.send_verification_code(
            user.email, code, self._settings.verification_code_lifetime
        )
