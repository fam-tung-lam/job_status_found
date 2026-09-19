"""Integration tests of `SmtpEmailSenderClient` with the real SMTP library and network."""

import pytest

from job_status_found.features.core import EmailDeliveryFailure, SmtpEmailSenderClient


async def test_an_unreachable_mail_server_fails_without_naming_the_recipient() -> None:
    # Given: a client pointed at a local port where no SMTP server listens.
    client = SmtpEmailSenderClient(
        hostname="127.0.0.1",
        port=1,
        security="none",
        username=None,
        password=None,
        from_address="JSV <no-reply@example.com>",
    )

    # When: an email is sent.
    # Then: delivery fails with the typed failure, whose message a caller may
    # log because it names neither the recipient nor the content.
    with pytest.raises(EmailDeliveryFailure) as failure:
        await client.send_plain_text_email(
            recipient="jane@example.com", subject="Code 123456", body="123456"
        )
    assert "jane@example.com" not in str(failure.value)
    assert "123456" not in str(failure.value)
