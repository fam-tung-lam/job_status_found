"""Unit tests of `SmtpAuthEmailSender` against a mock of the shared SMTP client."""

import logging
from datetime import timedelta

import pytest
from pytest_mock import MockerFixture

from job_status_found.features.auth.infrastructure.adapters.smtp_auth_email_sender import (
    SmtpAuthEmailSender,
)
from job_status_found.features.core import EmailDeliveryFailure, SmtpEmailSenderClient


class TestSmtpAuthEmailSender:
    """The auth email sender against an autospecced mock of the SMTP client."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Create a fresh client mock and the sender that delivers through it."""
        self.client = mocker.create_autospec(SmtpEmailSenderClient, instance=True)
        self.sender = SmtpAuthEmailSender(client=self.client)

    async def test_a_failed_delivery_is_logged_without_the_recipient_or_code(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Given: an SMTP client whose delivery fails.
        self.client.send.side_effect = EmailDeliveryFailure("SMTPConnectError: connection refused")

        # When: a verification code is sent.
        await self.sender.send_verification_code(
            "jane@example.com", "123456", timedelta(minutes=15)
        )

        # Then: the failure is logged as an error, not raised, naming the email
        # kind and the cause but neither the recipient nor the code.
        [record] = [r for r in caplog.records if r.levelno == logging.ERROR]
        message = record.getMessage()
        assert "verification code" in message
        assert "SMTPConnectError" in message
        assert "jane@example.com" not in message
        assert "123456" not in message
