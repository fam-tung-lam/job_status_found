from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, call, create_autospec
from uuid import uuid4

import pytest

from job_status_found.features.auth.application.dtos.new_email_challenge import (
    NewEmailChallenge,
)
from job_status_found.features.auth.application.dtos.sign_up_input import SignUpInput
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
from job_status_found.features.auth.application.use_cases.sign_up_with_password_use_case import (
    SignUpSettings,
    SignUpWithPasswordUseCase,
)
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.failures.sign_up_failure import SignUpPasswordTooWeak
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.auth.domain.value_objects.password_policy import PasswordPolicy
from job_status_found.features.core import Clock, UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
CODE_LIFETIME = timedelta(minutes=15)
SEND_INTERVAL = timedelta(seconds=60)
JUST_UNDER_THE_INTERVAL = SEND_INTERVAL - timedelta(microseconds=1)
UNVERIFIED_USER = User(id=uuid4(), email="Jane.Doe@Example.com", email_verified_at=None)
VERIFIED_USER = User(id=uuid4(), email="Jane.Doe@Example.com", email_verified_at=NOW)


def _sign_up(password: str = "second password") -> SignUpInput:
    """Build a sign-up for the shared email, with a chosen password."""
    return SignUpInput(
        first_name="Janet", last_name="Doe", email="Jane.Doe@Example.com", password=password
    )


class TestSignUpWithPasswordUseCase:
    """The sign-up use case against an autospecced mock of each port.

    Autospec makes a call that does not match a port's signature fail the test.
    """

    def setup_method(self) -> None:
        """Create fresh port mocks, stub what every test shares, and build the use case."""
        self.users = create_autospec(UserRepository, instance=True)
        self.password_credentials = create_autospec(PasswordCredentialRepository, instance=True)
        self.email_challenges = create_autospec(EmailChallengeRepository, instance=True)
        self.auth_events = create_autospec(AuthEventRepository, instance=True)
        self.unit_of_work = create_autospec(UnitOfWork, instance=True)
        self.password_hasher = create_autospec(PasswordHasher, instance=True)
        self.verification_code_generator = create_autospec(VerificationCodeGenerator, instance=True)
        self.verification_code_hasher = create_autospec(VerificationCodeHasher, instance=True)
        self.clock = create_autospec(Clock, instance=True)
        self.email_sender = create_autospec(AuthEmailSender, instance=True)

        self.clock.now.return_value = NOW
        self.password_hasher.hash.side_effect = lambda password: f"hashed:{password}"
        self.verification_code_generator.generate_verification_code.return_value = "012345"
        self.verification_code_hasher.hash_verification_code.side_effect = lambda code: (
            f"keyed:{code}".encode()
        )

        self.use_case = SignUpWithPasswordUseCase(
            users=self.users,
            password_credentials=self.password_credentials,
            email_challenges=self.email_challenges,
            auth_events=self.auth_events,
            unit_of_work=self.unit_of_work,
            password_hasher=self.password_hasher,
            verification_code_generator=self.verification_code_generator,
            verification_code_hasher=self.verification_code_hasher,
            clock=self.clock,
            email_sender=self.email_sender,
            settings=SignUpSettings(
                password_policy=PasswordPolicy(min_length=12),
                terms_version="2026-09-18",
                verification_code_lifetime=CODE_LIFETIME,
                email_send_interval=SEND_INTERVAL,
            ),
        )

    def teardown_method(self) -> None:
        """Clear every mock's calls and stubs, so no state reaches another test."""
        for port_mock in (
            self.users,
            self.password_credentials,
            self.email_challenges,
            self.auth_events,
            self.unit_of_work,
            self.password_hasher,
            self.verification_code_generator,
            self.verification_code_hasher,
            self.clock,
            self.email_sender,
        ):
            port_mock.reset_mock(return_value=True, side_effect=True)

    def _stub_existing_user(self, user: User) -> None:
        """Stub the users repository so the submitted email already belongs to `user`."""
        self.users.add_unverified.return_value = None
        self.users.lock_by_normalized_email.return_value = user

    async def test_the_code_is_mailed_only_after_the_writes_are_committed(self) -> None:
        # Given: no account exists, and one recorder that sees both the commit
        # and the email.
        self.users.add_unverified.return_value = UNVERIFIED_USER
        order = Mock()
        order.attach_mock(self.unit_of_work.commit, "commit")
        order.attach_mock(self.email_sender.send_verification_code, "send_verification_code")

        # When: a person signs up.
        await self.use_case.invoke(_sign_up())

        # Then: the one email goes out after the one commit, so it never names a
        # code that a rolled-back transaction discarded.
        assert order.mock_calls == [
            call.commit(),
            call.send_verification_code(UNVERIFIED_USER.email, "012345", CODE_LIFETIME),
        ]

    async def test_an_unverified_email_takes_the_new_password_and_code_once_the_interval_passed(
        self,
    ) -> None:
        # Given: an unverified account whose code was sent exactly one send
        # interval ago.
        self._stub_existing_user(UNVERIFIED_USER)
        self.email_challenges.find_latest_created_at.return_value = NOW - SEND_INTERVAL

        # When: someone signs up again with that email.
        await self.use_case.invoke(_sign_up())

        # Then: the new password replaces the first one, together with a new
        # code that replaces the open one and is mailed.
        self.password_credentials.save.assert_awaited_once_with(
            UNVERIFIED_USER.id, "hashed:second password", NOW
        )
        self.email_challenges.replace_open.assert_awaited_once_with(
            NewEmailChallenge(
                owner_id=UNVERIFIED_USER.id,
                purpose=EmailChallengePurpose.VERIFY_EMAIL,
                secret_hash=b"keyed:012345",
                created_at=NOW,
                expires_at=NOW + CODE_LIFETIME,
            )
        )
        self.email_sender.send_verification_code.assert_awaited_once_with(
            UNVERIFIED_USER.email, "012345", CODE_LIFETIME
        )

    async def test_an_unverified_email_within_the_interval_changes_nothing_and_sends_nothing(
        self,
    ) -> None:
        # Given: an unverified account whose code was sent just under one send
        # interval ago.
        self._stub_existing_user(UNVERIFIED_USER)
        self.email_challenges.find_latest_created_at.return_value = NOW - JUST_UNDER_THE_INTERVAL

        # When: someone signs up again with that email and another password.
        await self.use_case.invoke(_sign_up())

        # Then: the account, its password, and its open code stay as they were,
        # so the owner can only confirm the password the code was mailed for.
        self.users.update_registration.assert_not_awaited()
        self.password_credentials.save.assert_not_awaited()
        self.email_challenges.replace_open.assert_not_awaited()
        # And: no email goes out.
        self.email_sender.send_verification_code.assert_not_awaited()

    @pytest.mark.parametrize(
        ("last_notice_ago", "notified"),
        [(None, True), (JUST_UNDER_THE_INTERVAL, False), (SEND_INTERVAL, True)],
    )
    async def test_a_verified_email_gets_at_most_one_notice_per_send_interval(
        self, last_notice_ago: timedelta | None, notified: bool
    ) -> None:
        # Given: a verified account whose owner got no notice yet, or got one
        # just under or exactly one send interval ago.
        self._stub_existing_user(VERIFIED_USER)
        self.auth_events.find_latest_created_at.return_value = (
            None if last_notice_ago is None else NOW - last_notice_ago
        )

        # When: someone signs up with its email.
        await self.use_case.invoke(_sign_up())

        # Then: a notice goes out, and is recorded to pace the next one, only
        # once the interval has passed.
        sent = self.email_sender.send_existing_account_notice.await_args_list
        recorded = self.auth_events.record.await_args_list
        assert sent == ([call(VERIFIED_USER.email)] if notified else [])
        assert recorded == (
            [call(VERIFIED_USER.id, "existing_account_notice_sent", NOW)] if notified else []
        )
        # And: the account itself never changes.
        self.users.update_registration.assert_not_awaited()
        self.password_credentials.save.assert_not_awaited()

    async def test_a_password_outside_the_policy_is_refused_before_anything_is_stored_or_sent(
        self,
    ) -> None:
        # Given: a password one code point shorter than the policy allows.
        too_short = "x" * 11

        # When: a person signs up with it.
        # Then: the sign-up is refused before any hash, write, or email.
        with pytest.raises(SignUpPasswordTooWeak):
            await self.use_case.invoke(_sign_up(password=too_short))
        self.password_hasher.hash.assert_not_awaited()
        self.users.add_unverified.assert_not_awaited()
        self.email_sender.send_verification_code.assert_not_awaited()
