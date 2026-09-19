from unittest.mock import ANY, patch

import aiosmtplib
import pytest

from job_status_found.features.core import (
    EmailDeliveryFailure,
    SmtpEmailSenderClient,
    SmtpSecurity,
)


def _client(*, port: int = 587, security: SmtpSecurity = "none") -> SmtpEmailSenderClient:
    """Build a client for a local port with a chosen security setting."""
    return SmtpEmailSenderClient(
        hostname="127.0.0.1",
        port=port,
        security=security,
        username=None,
        password=None,
        sender="JSV <no-reply@example.com>",
    )


class TestSmtpEmailSenderClientWithStubbedSmtp:
    """The client with `aiosmtplib.send` patched, so each test controls the server's answer."""

    def setup_method(self) -> None:
        """Patch `aiosmtplib.send` with an autospecced mock that accepts every email."""
        self.send_patch = patch.object(aiosmtplib, "send", autospec=True)
        self.send = self.send_patch.start()

    def teardown_method(self) -> None:
        """Restore the real `aiosmtplib.send`."""
        self.send_patch.stop()

    @pytest.mark.parametrize(
        ("security", "implicit_tls", "starttls"),
        [("none", False, False), ("starttls", False, True), ("tls", True, False)],
    )
    async def test_each_security_setting_protects_the_connection_its_way(
        self, security: SmtpSecurity, implicit_tls: bool, starttls: bool
    ) -> None:
        # Given: a client with one security setting.
        client = _client(security=security)

        # When: an email is sent.
        await client.send(recipient="jane@example.com", subject="Hello", body="Hi Jane.")

        # Then: the connection uses implicit TLS, STARTTLS, or neither, as set.
        self.send.assert_awaited_once_with(
            ANY,
            hostname=ANY,
            port=ANY,
            username=None,
            password=None,
            use_tls=implicit_tls,
            start_tls=starttls,
            timeout=ANY,
        )

    @pytest.mark.parametrize(
        "rejection",
        [
            aiosmtplib.SMTPResponseException(550, "5.1.1 <jane@example.com>: Recipient rejected"),
            aiosmtplib.SMTPRecipientsRefused(
                [aiosmtplib.SMTPRecipientRefused(550, "5.1.1 Rejected", "jane@example.com")]
            ),
        ],
    )
    async def test_a_server_rejection_that_quotes_the_recipient_fails_without_it(
        self, rejection: aiosmtplib.SMTPException
    ) -> None:
        # Given: a server that rejects the email with a reply quoting the address.
        self.send.side_effect = rejection

        # When: an email is sent.
        # Then: the failure keeps the error type but drops the quoted address.
        with pytest.raises(EmailDeliveryFailure) as failure:
            await _client().send(recipient="jane@example.com", subject="Hello", body="Hi Jane.")
        assert type(rejection).__name__ in str(failure.value)
        assert "jane@example.com" not in str(failure.value)


async def test_an_unreachable_mail_server_fails_without_naming_the_recipient() -> None:
    # Given: a client pointed at a local port where no SMTP server listens.
    client = _client(port=1)

    # When: an email is sent.
    # Then: delivery fails with the typed failure, whose message a caller may
    # log because it names neither the recipient nor the content.
    with pytest.raises(EmailDeliveryFailure) as failure:
        await client.send(recipient="jane@example.com", subject="Code 123456", body="123456")
    assert "jane@example.com" not in str(failure.value)
    assert "123456" not in str(failure.value)
