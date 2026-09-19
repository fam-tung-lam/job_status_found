"""Unit tests of joint email-code and password confirmation."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.confirm_email_verification_input_dto import (
    ConfirmEmailVerificationInputDTO,
)
from job_status_found.features.auth.application.dtos.session_input_dto import SessionInputDTO
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
from job_status_found.features.auth.application.use_cases.confirm_email_verification_use_case import (  # noqa: E501
    ConfirmEmailVerificationUseCase,
    EmailVerificationSettings,
)
from job_status_found.features.auth.application.use_cases.issue_password_session_use_case import (
    IssuePasswordSessionUseCase,
)
from job_status_found.features.auth.domain.entities.email_challenge import EmailChallenge
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.failures.email_verification_failure import (
    EmailVerificationCodeInvalidFailure,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed confirmation instant."""


class TestConfirmEmailVerificationUseCase:
    """Joint proof, atomic success, and rolling failure exhaustion."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Build the use case with a mock of every collaborator."""
        self.users = mocker.create_autospec(UserRepository, instance=True)
        self.password_credentials = mocker.create_autospec(
            PasswordCredentialRepository, instance=True
        )
        self.email_challenges = mocker.create_autospec(EmailChallengeRepository, instance=True)
        self.auth_events = mocker.create_autospec(AuthEventRepository, instance=True)
        self.issue_password_session = mocker.create_autospec(
            IssuePasswordSessionUseCase, instance=True
        )
        self.unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        self.verify_password = mocker.async_stub(name="verify_and_update_password")
        self.hash_code = mocker.stub(name="hash_verification_code")
        self.compare_hashes = mocker.stub(name="are_hashes_equal")
        self.utc_now = mocker.stub(name="utc_now")
        self.utc_now.return_value = NOW
        self.hash_code.return_value = b"submitted"
        self.compare_hashes.side_effect = lambda expected, submitted: expected == submitted

        self.owner_id = uuid4()
        self.user = User(id=self.owner_id, email="Jane@example.com", email_verified_at=None)
        self.challenge = EmailChallenge(
            id=uuid4(),
            owner_id=self.owner_id,
            secret_hash=b"submitted",
            attempt_count=0,
            expires_at=NOW + timedelta(minutes=1),
            consumed_at=None,
        )
        self.users.lock_user_by_normalized_email.return_value = self.user
        self.password_credentials.find_password_hash.return_value = "real-hash"
        self.email_challenges.lock_open_email_challenge.return_value = self.challenge
        self.auth_events.count_auth_events_since.return_value = 0
        self.verify_password.return_value = (True, None)
        self.token_pair = TokenPairDTO(
            access_token="access",
            expires_in=900,
            refresh_token="refresh",
            client_kind=ClientKind.ANDROID,
            is_persistent=True,
        )
        self.issue_password_session.invoke.return_value = self.token_pair
        self.use_case = ConfirmEmailVerificationUseCase(
            users=self.users,
            password_credentials=self.password_credentials,
            email_challenges=self.email_challenges,
            auth_events=self.auth_events,
            issue_password_session=self.issue_password_session,
            unit_of_work=self.unit_of_work,
            verify_and_update_password=self.verify_password,
            hash_verification_code=self.hash_code,
            are_hashes_equal=self.compare_hashes,
            utc_now=self.utc_now,
            dummy_password_hash="dummy-hash",
            settings=EmailVerificationSettings(code_lifetime=timedelta(minutes=15)),
        )

    def _confirmation(self) -> ConfirmEmailVerificationInputDTO:
        """Build the shared valid confirmation input."""
        return ConfirmEmailVerificationInputDTO(
            email="Jane@example.com",
            code="123456",
            password="the matching password",
            session=SessionInputDTO(
                client_kind=ClientKind.ANDROID,
                remember_me=True,
                ip_address=None,
                user_agent=None,
            ),
        )

    @pytest.mark.asyncio
    async def test_a_matching_code_and_password_are_consumed_before_one_session_commits(
        self,
    ) -> None:
        """
        Given: an unexpired code and its matching account password.
        When: the person confirms them together.
        Then: the challenge and email are consumed and one session commits.
        """
        # Given: an unexpired code and its matching account password.
        confirmation = self._confirmation()

        # When: the person confirms them together.
        result = await self.use_case.invoke(confirmation)

        # Then: the challenge and email are consumed and one session commits.
        assert result == self.token_pair
        self.email_challenges.consume_email_challenge.assert_awaited_once_with(
            self.challenge.id, NOW
        )
        self.users.set_email_verified_at.assert_awaited_once_with(self.owner_id, NOW)
        self.issue_password_session.invoke.assert_awaited_once()
        self.unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_the_fifth_recent_failed_pair_consumes_a_replaced_challenge_and_commits(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Given: four recent failures across prior challenge replacements.
        When: another code-password pair fails against the current challenge.
        Then: the rolling fifth failure is recorded and consumes the challenge before rejection.
        """
        # Given: four recent failures across prior challenge replacements.
        self.auth_events.count_auth_events_since.return_value = 4
        self.verify_password.return_value = (False, None)
        caplog.set_level("WARNING")

        # When: another code-password pair fails against the current challenge.
        # Then: the fifth failure is persisted before the generic rejection.
        with pytest.raises(EmailVerificationCodeInvalidFailure):
            await self.use_case.invoke(self._confirmation())
        self.auth_events.create_auth_event.assert_awaited_once()
        self.email_challenges.register_wrong_email_challenge_answer.assert_awaited_once_with(
            self.challenge.id, attempt_count=1, consumed_at=NOW
        )
        self.unit_of_work.commit.assert_awaited_once()
        self.issue_password_session.invoke.assert_not_awaited()
        assert len(caplog.records) == 1
        assert str(self.owner_id) in caplog.records[0].message
        assert "123456" not in caplog.records[0].message
        assert "the matching password" not in caplog.records[0].message

    @pytest.mark.asyncio
    async def test_an_unknown_email_still_pays_for_one_dummy_password_verification(self) -> None:
        """
        Given: an email with no account.
        When: a confirmation is submitted.
        Then: one dummy Argon2id check runs and the generic failure follows after commit.
        """
        # Given: an email with no account.
        self.users.lock_user_by_normalized_email.return_value = None
        self.verify_password.return_value = (False, None)

        # When: a confirmation is submitted.
        # Then: one dummy Argon2id check runs and the generic failure follows after commit.
        with pytest.raises(EmailVerificationCodeInvalidFailure):
            await self.use_case.invoke(self._confirmation())
        self.verify_password.assert_awaited_once_with("the matching password", "dummy-hash")
        self.auth_events.create_auth_event.assert_not_awaited()
        self.unit_of_work.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_a_code_expiring_exactly_now_is_rejected_and_committed(self) -> None:
        """
        Given: the jointly matching code and password but an expiry equal to now.
        When: confirmation runs.
        Then: the expiry boundary is invalid and the failed proof commits.
        """
        # Given: the jointly matching code and password but an expiry equal to now.
        self.email_challenges.lock_open_email_challenge.return_value = EmailChallenge(
            id=self.challenge.id,
            owner_id=self.owner_id,
            secret_hash=b"submitted",
            attempt_count=0,
            expires_at=NOW,
            consumed_at=None,
        )

        # When: confirmation runs.
        # Then: the expiry boundary is invalid and the failed proof commits.
        with pytest.raises(EmailVerificationCodeInvalidFailure):
            await self.use_case.invoke(self._confirmation())
        self.issue_password_session.invoke.assert_not_awaited()
        self.auth_events.create_auth_event.assert_awaited_once()
        self.unit_of_work.commit.assert_awaited_once()
