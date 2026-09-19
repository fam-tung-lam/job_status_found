"""Plain-text email delivery through an SMTP server, for every feature."""

from email.message import EmailMessage
from typing import Literal

import aiosmtplib

type SmtpSecurity = Literal["none", "starttls", "tls"]
"""How the connection is protected: in the clear, upgraded with STARTTLS, or implicit TLS."""

_SMTP_TIMEOUT_SECONDS = 10
"""Seconds one SMTP operation may take before delivery fails, so a slow server never hangs."""


class EmailDeliveryFailure(Exception):
    """The SMTP server could not be reached, or it refused the email.

    The message names the SMTP error but never the recipient, so a caller may
    log it.
    """


class SmtpEmailSenderClient:
    """Sends plain-text emails, each over its own SMTP connection.

    A feature's email adapter composes its messages and sends them through
    this client; the client knows nothing about what an email says.
    """

    def __init__(  # noqa: PLR0913 - one value per SMTP setting reads better than a wrapper type
        self,
        *,
        hostname: str,
        port: int,
        security: SmtpSecurity,
        username: str | None,
        password: str | None,
        sender: str,
    ) -> None:
        """Deliver through one SMTP server.

        Args:
            hostname: SMTP server host name.
            port: SMTP server TCP port.
            security: How the connection is protected.
            username: SMTP user name; `None` skips authentication.
            password: Password for `username`.
            sender: The `From` address of every email.
        """
        self._hostname = hostname
        self._port = port
        self._security = security
        self._username = username
        self._password = password
        self._sender = sender

    async def send(self, *, recipient: str, subject: str, body: str) -> None:
        """Send one plain-text email and wait until the server accepts it.

        Args:
            recipient: The address to deliver to.
            subject: The subject line.
            body: The plain-text body.

        Raises:
            EmailDeliveryFailure: The server was unreachable, timed out, or
                refused the email.
        """
        message = EmailMessage()
        message["From"] = self._sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        try:
            await aiosmtplib.send(
                message,
                hostname=self._hostname,
                port=self._port,
                username=self._username,
                password=self._password,
                use_tls=self._security == "tls",
                start_tls=self._security == "starttls",
                timeout=_SMTP_TIMEOUT_SECONDS,
            )
        except (aiosmtplib.SMTPException, OSError) as error:
            raise EmailDeliveryFailure(_describe(error)) from error


def _describe(error: aiosmtplib.SMTPException | OSError) -> str:
    """Describe an SMTP error without any recipient address it may quote.

    A server reply or a refused recipient can quote the address, so those keep
    only their type and reply code.

    Args:
        error: The error the SMTP library raised.

    Returns:
        A description that is safe to log.
    """
    if isinstance(error, aiosmtplib.SMTPResponseException):
        return f"{type(error).__name__} {error.code}"
    if isinstance(error, aiosmtplib.SMTPRecipientsRefused):
        return type(error).__name__
    return f"{type(error).__name__}: {error}"
