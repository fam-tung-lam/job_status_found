"""Unit tests of enumeration-safe verification-code resend."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.new_email_challenge_dto import (
    NewEmailChallengeDTO,
)
from job_status_found.features.auth.application.ports.auth_email_sender import AuthEmailSender
from job_status_found.features.auth.application.ports.email_challenge_repository import (
    EmailChallengeRepository,
)
from job_status_found.features.auth.application.ports.user_repository import UserRepository
from job_status_found.features.auth.application.use_cases.resend_email_verification_use_case import (  # noqa: E501
    ResendEmailVerificationSettings,
    ResendEmailVerificationUseCase,
)
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.value_objects.email_challenge_purpose import (
    EmailChallengePurpose,
)
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed resend instant."""


class TestResendEmailVerificationUseCase:
    """Identical outcomes and paced replacement mail."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Build resend with a mock of each collaborator."""
        self.users = mocker.create_autospec(UserRepository, instance=True)
        self.challenges = mocker.create_autospec(EmailChallengeRepository, instance=True)
        self.unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        self.sender = mocker.create_autospec(AuthEmailSender, instance=True)
        self.generate_code = mocker.stub(name="generate_verification_code")
        self.hash_code = mocker.stub(name="hash_verification_code")
        self.utc_now = mocker.stub(name="utc_now")
        self.generate_code.return_value = "123456"
        self.hash_code.return_value = b"hash"
        self.utc_now.return_value = NOW
        self.use_case = ResendEmailVerificationUseCase(
            users=self.users,
            email_challenges=self.challenges,
            unit_of_work=self.unit_of_work,
            generate_verification_code=self.generate_code,
            hash_verification_code=self.hash_code,
            utc_now=self.utc_now,
            email_sender=self.sender,
            settings=ResendEmailVerificationSettings(
                code_lifetime=timedelta(minutes=15), send_interval=timedelta(seconds=60)
            ),
        )

    @pytest.mark.asyncio
    async def test_an_unknown_email_commits_the_same_empty_outcome_without_mail(self) -> None:
        """
        Given: an email with no account.
        When: resend is requested.
        Then: the transaction ends but no code is stored or mailed.
        """
        # Given: an email with no account.
        self.users.lock_user_by_normalized_email.return_value = None

        # When: resend is requested.
        await self.use_case.invoke("unknown@example.com")

        # Then: the transaction ends but no code is stored or mailed.
        self.unit_of_work.commit.assert_awaited_once()
        self.challenges.replace_open_email_challenge.assert_not_awaited()
        self.sender.send_verification_code.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_an_unverified_email_after_the_interval_is_replaced_then_mailed(self) -> None:
        """
        Given: an unverified account whose last code is one interval old.
        When: resend is requested.
        Then: the replacement commits before its clear code is queued for mail.
        """
        # Given: an unverified account whose last code is one interval old.
        user = User(id=uuid4(), email="Jane@example.com", email_verified_at=None)
        self.users.lock_user_by_normalized_email.return_value = user
        self.challenges.find_last_email_challenge_sent_at.return_value = NOW - timedelta(seconds=60)

        # When: resend is requested.
        await self.use_case.invoke("Jane@example.com")

        # Then: the replacement commits and its clear code is queued for mail.
        self.challenges.replace_open_email_challenge.assert_awaited_once_with(
            NewEmailChallengeDTO(
                owner_id=user.id,
                purpose=EmailChallengePurpose.VERIFY_EMAIL,
                secret_hash=b"hash",
                created_at=NOW,
                expires_at=NOW + timedelta(minutes=15),
            )
        )
        self.unit_of_work.commit.assert_awaited_once()
        self.sender.send_verification_code.assert_awaited_once_with(
            user.email, "123456", timedelta(minutes=15)
        )

    @pytest.mark.parametrize("is_verified", [False, True], ids=["inside-interval", "verified"])
    @pytest.mark.asyncio
    async def test_a_recent_or_verified_email_commits_without_replacement_or_mail(
        self, is_verified: bool
    ) -> None:
        """
        Given: an unverified account inside the interval, or a verified account.
        When: resend is requested.
        Then: the same no-mail outcome commits without changing a challenge.
        """
        # Given: an unverified account inside the interval, or a verified account.
        user = User(
            id=uuid4(),
            email="Jane@example.com",
            email_verified_at=NOW if is_verified else None,
        )
        self.users.lock_user_by_normalized_email.return_value = user
        self.challenges.find_last_email_challenge_sent_at.return_value = NOW

        # When: resend is requested.
        await self.use_case.invoke(user.email)

        # Then: the same no-mail outcome commits without changing a challenge.
        self.challenges.replace_open_email_challenge.assert_not_awaited()
        self.sender.send_verification_code.assert_not_awaited()
        self.unit_of_work.commit.assert_awaited_once()
