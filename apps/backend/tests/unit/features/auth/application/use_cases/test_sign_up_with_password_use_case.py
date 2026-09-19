"""Unit tests of `SignUpWithPasswordUseCase` against a mock of each collaborator."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

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
from job_status_found.features.auth.application.ports.user_repository import UserRepository
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
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The instant the stubbed `utc_now` tells for every sign-up."""

CODE_LIFETIME = timedelta(minutes=15)
"""How long a verification code stays valid under the test settings."""

SEND_INTERVAL = timedelta(seconds=60)
"""Shortest time between two sign-up emails to one user under the test settings."""

JUST_UNDER_THE_INTERVAL = SEND_INTERVAL - timedelta(microseconds=1)
"""The longest gap that is still inside the send interval."""

UNVERIFIED_USER = User(id=uuid4(), email="Jane.Doe@Example.com", email_verified_at=None)
"""An account whose owner has not confirmed the email yet."""

VERIFIED_USER = User(id=uuid4(), email="Jane.Doe@Example.com", email_verified_at=NOW)
"""An account whose owner confirmed the email."""


def _sign_up(password: str = "second password") -> SignUpInput:
    """Build a sign-up for the shared email, with a chosen password."""
    return SignUpInput(
        first_name="Janet", last_name="Doe", email="Jane.Doe@Example.com", password=password
    )


class TestSignUpWithPasswordUseCase:
    """The sign-up use case against a mock of each port and injected helper function.

    Autospec makes a call that does not match a port's signature fail the test;
    ty checks the calls to each helper against the use case's `Callable` types.
    """

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Create fresh mocks, stub what every test shares, and build the use case."""
        self.users = mocker.create_autospec(UserRepository, instance=True)
        self.password_credentials = mocker.create_autospec(
            PasswordCredentialRepository, instance=True
        )
        self.email_challenges = mocker.create_autospec(EmailChallengeRepository, instance=True)
        self.auth_events = mocker.create_autospec(AuthEventRepository, instance=True)
        self.unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        self.email_sender = mocker.create_autospec(AuthEmailSender, instance=True)
        self.hash_password = mocker.async_stub(name="hash_password")
        self.generate_verification_code = mocker.stub(name="generate_verification_code")
        self.hash_verification_code = mocker.stub(name="hash_verification_code")
        self.utc_now = mocker.stub(name="utc_now")

        self.hash_password.side_effect = lambda password: f"hashed:{password}"
        self.generate_verification_code.return_value = "012345"
        self.hash_verification_code.side_effect = lambda code: f"keyed:{code}".encode()
        self.utc_now.return_value = NOW

        self.use_case = SignUpWithPasswordUseCase(
            users=self.users,
            password_credentials=self.password_credentials,
            email_challenges=self.email_challenges,
            auth_events=self.auth_events,
            unit_of_work=self.unit_of_work,
            hash_password=self.hash_password,
            generate_verification_code=self.generate_verification_code,
            hash_verification_code=self.hash_verification_code,
            utc_now=self.utc_now,
            email_sender=self.email_sender,
            settings=SignUpSettings(
                password_policy=PasswordPolicy(min_length=12),
                terms_version="2026-09-18",
                verification_code_lifetime=CODE_LIFETIME,
                email_send_interval=SEND_INTERVAL,
            ),
        )

    def _stub_existing_user(self, user: User) -> None:
        """Stub the users repository so the submitted email already belongs to `user`."""
        self.users.add_unverified.return_value = None
        self.users.lock_by_normalized_email.return_value = user

    async def test_the_code_is_mailed_only_after_the_writes_are_committed(
        self, mocker: MockerFixture
    ) -> None:
        # Given: no account exists, and one recorder that sees both the commit
        # and the email.
        self.users.add_unverified.return_value = UNVERIFIED_USER
        order = mocker.Mock()
        order.attach_mock(self.unit_of_work.commit, "commit")
        order.attach_mock(self.email_sender.send_verification_code, "send_verification_code")

        # When: a person signs up.
        await self.use_case.invoke(_sign_up())

        # Then: the one email goes out after the one commit, so it never names a
        # code that a rolled-back transaction discarded.
        assert order.mock_calls == [
            mocker.call.commit(),
            mocker.call.send_verification_code(UNVERIFIED_USER.email, "012345", CODE_LIFETIME),
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
        "last_notice_at",
        [None, NOW - SEND_INTERVAL],
        ids=["no-notice-yet", "notice-one-interval-ago"],
    )
    async def test_a_verified_email_gets_a_recorded_notice_once_the_interval_passed(
        self, last_notice_at: datetime | None
    ) -> None:
        # Given: a verified account whose owner got no notice yet, or got one
        # exactly one send interval ago.
        self._stub_existing_user(VERIFIED_USER)
        self.auth_events.find_latest_created_at.return_value = last_notice_at

        # When: someone signs up with its email.
        await self.use_case.invoke(_sign_up())

        # Then: the owner gets a notice, recorded to pace the next one.
        self.email_sender.send_existing_account_notice.assert_awaited_once_with(VERIFIED_USER.email)
        self.auth_events.record.assert_awaited_once_with(
            VERIFIED_USER.id, "existing_account_notice_sent", NOW
        )
        # And: the account itself never changes.
        self.users.update_registration.assert_not_awaited()
        self.password_credentials.save.assert_not_awaited()

    async def test_a_verified_email_within_the_interval_gets_no_second_notice(self) -> None:
        # Given: a verified account whose owner got a notice just under one send
        # interval ago.
        self._stub_existing_user(VERIFIED_USER)
        self.auth_events.find_latest_created_at.return_value = NOW - JUST_UNDER_THE_INTERVAL

        # When: someone signs up with its email.
        await self.use_case.invoke(_sign_up())

        # Then: no notice goes out and none is recorded.
        self.email_sender.send_existing_account_notice.assert_not_awaited()
        self.auth_events.record.assert_not_awaited()

    async def test_a_password_outside_the_policy_is_refused_before_anything_is_stored_or_sent(
        self,
    ) -> None:
        # Given: a password one code point shorter than the policy allows.
        too_short = "x" * 11

        # When: a person signs up with it.
        # Then: the sign-up is refused before any hash, write, or email.
        with pytest.raises(SignUpPasswordTooWeak):
            await self.use_case.invoke(_sign_up(password=too_short))
        self.hash_password.assert_not_awaited()
        self.users.add_unverified.assert_not_awaited()
        self.email_sender.send_verification_code.assert_not_awaited()
