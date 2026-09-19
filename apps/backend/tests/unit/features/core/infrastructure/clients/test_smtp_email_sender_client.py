"""Unit tests of `SmtpEmailSenderClient` with the SMTP library's send patched."""

import aiosmtplib
import pytest
from pytest_mock import MockerFixture

from job_status_found.features.core import (
    EmailDeliveryFailure,
    SmtpEmailSenderClient,
    SmtpSecurity,
)


def _build_smtp_client(*, security: SmtpSecurity = "none") -> SmtpEmailSenderClient:
    """Build a client for a local server with a chosen security setting."""
    return SmtpEmailSenderClient(
        hostname="127.0.0.1",
        port=587,
        security=security,
        username=None,
        password=None,
        from_address="JSV <no-reply@example.com>",
    )


class TestSmtpEmailSenderClient:
    """The client with `aiosmtplib.send` patched, so each test controls the server's answer."""

    @pytest.fixture(autouse=True)
    def _set_up(self, mocker: MockerFixture) -> None:
        """Patch `aiosmtplib.send` with an autospecced mock that accepts every email.

        The client looks `send` up on the `aiosmtplib` module at call time, so
        the module attribute is where to patch. `mocker` restores it after the
        test.
        """
        self.aiosmtplib_send = mocker.patch.object(aiosmtplib, "send", autospec=True)

    @pytest.mark.parametrize(
        ("security", "implicit_tls", "starttls"),
        [("none", False, False), ("starttls", False, True), ("tls", True, False)],
    )
    async def test_each_security_setting_protects_the_connection_its_way(
        self, security: SmtpSecurity, implicit_tls: bool, starttls: bool
    ) -> None:
        # Given: a client with one security setting.
        client = _build_smtp_client(security=security)

        # When: an email is sent.
        await client.send_plain_text_email(
            recipient="jane@example.com", subject="Hello", body="Hi Jane."
        )

        # Then: the one connection uses implicit TLS, STARTTLS, or neither, as set.
        [send_call] = self.aiosmtplib_send.await_args_list
        assert (send_call.kwargs["use_tls"], send_call.kwargs["start_tls"]) == (
            implicit_tls,
            starttls,
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
        self.aiosmtplib_send.side_effect = rejection

        # When: an email is sent.
        # Then: the failure keeps the error type but drops the quoted address.
        with pytest.raises(EmailDeliveryFailure) as failure:
            await _build_smtp_client().send_plain_text_email(
                recipient="jane@example.com", subject="Hello", body="Hi Jane."
            )
        assert type(rejection).__name__ in str(failure.value)
        assert "jane@example.com" not in str(failure.value)
