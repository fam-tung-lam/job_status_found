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
        self.smtp_client = mocker.create_autospec(SmtpEmailSenderClient, instance=True)
        self.auth_email_sender = SmtpAuthEmailSender(smtp_client=self.smtp_client)

    async def test_a_failed_delivery_is_logged_without_the_recipient_or_code(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Given: an SMTP client whose delivery fails.
        self.smtp_client.send_plain_text_email.side_effect = EmailDeliveryFailure(
            "SMTPConnectError: connection refused"
        )

        # When: a verification code is sent.
        await self.auth_email_sender.send_verification_code(
            "jane@example.com", "123456", timedelta(minutes=15)
        )

        # Then: the failure is logged as an error, not raised, naming the email
        # kind and the cause but neither the recipient nor the code.
        [error_record] = [
            log_record for log_record in caplog.records if log_record.levelno == logging.ERROR
        ]
        message = error_record.getMessage()
        assert "verification code" in message
        assert "SMTPConnectError" in message
        assert "jane@example.com" not in message
        assert "123456" not in message
