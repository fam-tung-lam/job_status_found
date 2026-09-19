"""Unit tests of password sign-in decisions."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.application.dtos.password_sign_in_input import (
    PasswordSignInInput,
)
from job_status_found.features.auth.application.dtos.session_input import SessionInput
from job_status_found.features.auth.application.dtos.token_pair import TokenPair
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
from job_status_found.features.auth.application.use_cases.sign_in_with_password_use_case import (
    PasswordSignInSettings,
    SignInWithPasswordUseCase,
)
from job_status_found.features.auth.domain.entities.user import User
from job_status_found.features.auth.domain.failures.password_sign_in_failure import (
    PasswordSignInInvalidCredentials,
)
from job_status_found.features.auth.domain.value_objects.client_kind import ClientKind
from job_status_found.features.auth.domain.value_objects.user_role import UserRole
from job_status_found.features.core import UnitOfWork

NOW = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
"""The fixed sign-in instant."""


class TestSignInWithPasswordUseCase:
    """Unknown-account equalization and durable failure audit."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Build password sign-in with a mock of every collaborator."""
        self.users = mocker.create_autospec(UserRepository, instance=True)
        self.password_credentials = mocker.create_autospec(
            PasswordCredentialRepository, instance=True
        )
        self.challenges = mocker.create_autospec(EmailChallengeRepository, instance=True)
        self.events = mocker.create_autospec(AuthEventRepository, instance=True)
        self.issue_password_session = mocker.create_autospec(
            IssuePasswordSessionUseCase, instance=True
        )
        self.unit_of_work = mocker.create_autospec(UnitOfWork, instance=True)
        self.sender = mocker.create_autospec(AuthEmailSender, instance=True)
        self.verify_password = mocker.async_stub(name="verify_and_update_password")
        self.hash_identifier = mocker.stub(name="hash_auth_identifier")
        self.generate_code = mocker.stub(name="generate_verification_code")
        self.hash_code = mocker.stub(name="hash_verification_code")
        self.utc_now = mocker.stub(name="utc_now")
        self.hash_identifier.return_value = b"identifier-hash"
        self.utc_now.return_value = NOW
        self.use_case = SignInWithPasswordUseCase(
            users=self.users,
            password_credentials=self.password_credentials,
            email_challenges=self.challenges,
            auth_events=self.events,
            issue_password_session=self.issue_password_session,
            unit_of_work=self.unit_of_work,
            verify_and_update_password=self.verify_password,
            hash_auth_identifier=self.hash_identifier,
            generate_verification_code=self.generate_code,
            hash_verification_code=self.hash_code,
            utc_now=self.utc_now,
            email_sender=self.sender,
            dummy_password_hash="dummy-hash",
            settings=PasswordSignInSettings(
                verification_code_lifetime=timedelta(minutes=15),
                verification_code_send_interval=timedelta(seconds=60),
            ),
        )

    def _sign_in(self) -> PasswordSignInInput:
        """Build the shared password and persistent iOS session input."""
        return PasswordSignInInput(
            email="Jane@example.com",
            password="submitted password",
            session=SessionInput(
                client_kind=ClientKind.IOS,
                remember_me=True,
                ip_address=None,
                user_agent="test",
            ),
        )

    @pytest.mark.asyncio
    async def test_an_unknown_email_runs_dummy_argon2_and_commits_one_hashed_event(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Given: an email with no account.
        When: password sign-in is attempted.
        Then: one dummy verification and one identifier-hashed event commit before rejection.
        """
        # Given: an email with no account and mocks for every collaborator.
        self.users.lock_user_by_normalized_email.return_value = None
        self.verify_password.return_value = (False, None)
        sign_in = PasswordSignInInput(
            email="Unknown@example.com",
            password="submitted password",
            session=SessionInput(
                client_kind=ClientKind.IOS,
                remember_me=True,
                ip_address=None,
                user_agent="test",
            ),
        )
        caplog.set_level("WARNING")

        # When: password sign-in is attempted.
        # Then: one dummy verification and event commit before generic rejection.
        with pytest.raises(PasswordSignInInvalidCredentials):
            await self.use_case.invoke(sign_in)
        self.verify_password.assert_awaited_once_with("submitted password", "dummy-hash")
        self.hash_identifier.assert_called_once_with("unknown@example.com")
        self.events.create_auth_event.assert_awaited_once()
        self.unit_of_work.commit.assert_awaited_once()
        self.issue_password_session.invoke.assert_not_awaited()
        assert len(caplog.records) == 1
        assert b"identifier-hash".hex() in caplog.records[0].message
        assert "unknown@example.com" not in caplog.records[0].message.lower()
        assert "submitted password" not in caplog.records[0].message

    @pytest.mark.asyncio
    async def test_a_social_only_account_runs_the_same_dummy_verifier_and_stays_generic(
        self,
    ) -> None:
        """
        Given: a verified account has no password credential.
        When: password sign-in is attempted.
        Then: one dummy verification runs and invalid_credentials is returned after commit.
        """
        # Given: a verified account has no password credential.
        owner_id = uuid4()
        self.users.lock_user_by_normalized_email.return_value = User(
            id=owner_id,
            email="Jane@example.com",
            email_verified_at=NOW,
        )
        self.password_credentials.find_password_hash.return_value = None
        self.verify_password.return_value = (True, None)

        # When: password sign-in is attempted.
        # Then: one dummy verification runs and invalid_credentials is returned after commit.
        with pytest.raises(PasswordSignInInvalidCredentials):
            await self.use_case.invoke(self._sign_in())
        self.verify_password.assert_awaited_once_with("submitted password", "dummy-hash")
        self.events.create_auth_event.assert_awaited_once()
        self.unit_of_work.commit.assert_awaited_once()
        self.issue_password_session.invoke.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_success_rehashes_the_real_password_before_the_session_commits(self) -> None:
        """
        Given: a verified password account whose Argon2 parameters need strengthening.
        When: its real password succeeds.
        Then: the replacement hash and session are written in the same commit.
        """
        # Given: a verified password account whose Argon2 parameters need strengthening.
        owner_id = uuid4()
        user = User(
            id=owner_id,
            email="Jane@example.com",
            email_verified_at=NOW,
            role=UserRole.USER,
        )
        token_pair = TokenPair(
            access_token="access",
            expires_in=900,
            refresh_token="refresh",
            client_kind=ClientKind.IOS,
            is_persistent=True,
        )
        self.users.lock_user_by_normalized_email.return_value = user
        self.password_credentials.find_password_hash.return_value = "old-real-hash"
        self.verify_password.return_value = (True, "strengthened-real-hash")
        self.issue_password_session.invoke.return_value = token_pair
        sign_in = self._sign_in()

        # When: its real password succeeds.
        result = await self.use_case.invoke(sign_in)

        # Then: the replacement hash and session are written in the same commit.
        assert result == token_pair
        self.verify_password.assert_awaited_once_with("submitted password", "old-real-hash")
        self.password_credentials.set_password_hash.assert_awaited_once_with(
            owner_id, "strengthened-real-hash", NOW
        )
        self.issue_password_session.invoke.assert_awaited_once_with(
            owner_id, UserRole.USER, sign_in.session, NOW
        )
        self.events.create_auth_event.assert_not_awaited()
        self.unit_of_work.commit.assert_awaited_once()
