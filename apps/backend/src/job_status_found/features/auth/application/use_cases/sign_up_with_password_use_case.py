"""Create an account with email and password, or email its owner instead."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from job_status_found.features.auth.application.dtos.new_email_challenge import (
    NewEmailChallenge,
)
from job_status_found.features.auth.application.dtos.sign_up_input import SignUpInput
from job_status_found.features.auth.application.dtos.user_registration import UserRegistration
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
from job_status_found.features.auth.application.ports.password_hasher import PasswordHasher
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.application.ports.verification_code_generator import (
    VerificationCodeGenerator,
)
from job_status_found.features.auth.application.ports.verification_code_hasher import (
    VerificationCodeHasher,
)
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.failures.sign_up_failure import SignUpPasswordTooWeak
from job_status_found.features.auth.domain.value_objects.email_address import EmailAddress
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy
from job_status_found.features.core import Clock, UnitOfWork

logger = logging.getLogger(__name__)

EXISTING_ACCOUNT_NOTICE_SENT = "existing_account_notice_sent"
"""`auth_events.event_type` of a notice sent to a verified account's owner."""


@dataclass(frozen=True, slots=True)
class SignUpSettings:
    """The configured rules a sign-up applies."""

    password_policy: PasswordPolicy
    """The length bounds a new password must meet."""

    terms_version: str
    """Version of the terms a person accepts by signing up."""

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
        password_hasher: PasswordHasher,
        verification_code_generator: VerificationCodeGenerator,
        verification_code_hasher: VerificationCodeHasher,
        clock: Clock,
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
            password_hasher: Hashes the password with Argon2id.
            verification_code_generator: Creates verification codes.
            verification_code_hasher: Hashes verification codes with the server key.
            clock: Tells the current instant.
            email_sender: Delivers the code or the notice.
            settings: The configured rules.
        """
        self._users = users
        self._password_credentials = password_credentials
        self._email_challenges = email_challenges
        self._auth_events = auth_events
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._verification_code_generator = verification_code_generator
        self._verification_code_hasher = verification_code_hasher
        self._clock = clock
        self._email_sender = email_sender
        self._settings = settings

    async def invoke(self, sign_up: SignUpInput) -> None:
        """Sign a person up, committing once and emailing after the commit.

        Args:
            sign_up: What the person submitted.

        Raises:
            SignUpPasswordTooWeak: The password's length is outside the policy.
            RuntimeError: The account holding the email was deleted while this
                sign-up ran.
        """
        policy = self._settings.password_policy
        if not policy.validate(sign_up.password):
            raise SignUpPasswordTooWeak(min_length=policy.min_length, max_length=policy.max_length)
        password_hash = await self._password_hasher.hash(sign_up.password)
        now = self._clock.now()
        registration = UserRegistration(
            email=EmailAddress(sign_up.email),
            first_name=sign_up.first_name,
            last_name=sign_up.last_name,
            terms_version=self._settings.terms_version,
            registered_at=now,
        )

        new_user = await self._users.add_unverified(registration)
        if new_user is not None:
            await self._finish_new_user(new_user, password_hash, now)
            return
        existing_user = await self._users.lock_by_normalized_email(registration.email.normalized)
        if existing_user is None:
            msg = "The account holding the signed-up email was deleted during the sign-up."
            raise RuntimeError(msg)
        if existing_user.is_email_verified:
            await self._finish_verified_user(existing_user, now)
        else:
            await self._finish_unverified_user(existing_user, registration, password_hash, now)

    async def _finish_new_user(self, user: User, password_hash: str, now: datetime) -> None:
        """Give a just-created account its password and first code, commit, then mail the code.

        Args:
            user: The account `add_unverified` just created.
            password_hash: The Argon2id hash of the submitted password.
            now: The instant of this sign-up.
        """
        await self._password_credentials.save(user.id, password_hash, now)
        code = await self._open_verification_code(user.id, now)
        await self._unit_of_work.commit()
        logger.info("Sign-up created unverified user %s", user.id)
        await self._send_verification_code(user, code)

    async def _finish_verified_user(self, user: User, now: datetime) -> None:
        """Leave a verified account unchanged; mail its owner a notice at most once per interval.

        Args:
            user: The verified account that owns the submitted email.
            now: The instant of this sign-up.
        """
        last_notice_at = await self._auth_events.find_latest_created_at(
            user.id, EXISTING_ACCOUNT_NOTICE_SENT
        )
        send_notice = self._interval_passed(last_notice_at, now)
        if send_notice:
            await self._auth_events.record(user.id, EXISTING_ACCOUNT_NOTICE_SENT, now)
        # Also ends the transaction that locked the row when nothing was written.
        await self._unit_of_work.commit()
        logger.info("Sign-up matched verified user %s; notice sent: %s", user.id, send_notice)
        if send_notice:
            await self._email_sender.send_existing_account_notice(user.email)

    async def _finish_unverified_user(
        self, user: User, registration: UserRegistration, password_hash: str, now: datetime
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
        last_code_at = await self._email_challenges.find_latest_created_at(
            user.id, EmailChallengePurpose.VERIFY_EMAIL
        )
        if not self._interval_passed(last_code_at, now):
            await self._unit_of_work.commit()
            logger.info("Sign-up left unverified user %s unchanged within the interval", user.id)
            return
        await self._users.update_registration(user.id, registration)
        await self._password_credentials.save(user.id, password_hash, now)
        code = await self._open_verification_code(user.id, now)
        await self._unit_of_work.commit()
        logger.info("Sign-up replaced the password and code of unverified user %s", user.id)
        await self._send_verification_code(user, code)

    def _interval_passed(self, last_sent_at: datetime | None, now: datetime) -> bool:
        """Tell whether another sign-up email may go out to the same user.

        Args:
            last_sent_at: When the last code or notice was sent; `None` if never.
            now: The instant of this sign-up.

        Returns:
            Whether a full send interval has passed, counting its end as passed.
        """
        return last_sent_at is None or now >= last_sent_at + self._settings.email_send_interval

    async def _open_verification_code(self, user_id: UUID, now: datetime) -> str:
        """Create a code and store its keyed hash, replacing the user's open code.

        Args:
            user_id: The user the code is for.
            now: The instant the code is issued; it expires one lifetime later.

        Returns:
            The code in the clear, to mail after the commit.
        """
        code = self._verification_code_generator.generate_verification_code()
        await self._email_challenges.replace_open(
            NewEmailChallenge(
                owner_id=user_id,
                purpose=EmailChallengePurpose.VERIFY_EMAIL,
                secret_hash=self._verification_code_hasher.hash_verification_code(code),
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
